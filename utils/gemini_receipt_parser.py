"""Receipt parsing powered by the Gemini API.

This module sends receipt images to Google's Gemini models and returns
structured data for each line item.  It follows the behaviour of the working
``testfactura.py`` script supplied by the user while keeping a small surface
area required by the rest of the project.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

# Insecure: embedded API key for demonstration purposes
API_KEY = "AIzaSyBS-RvRzXXhnm2rdPKgtpmUy_CIBTIp63o"


def get_gemini_api_key() -> str:
    """Return the Gemini API key.

    The key is hardcoded for convenience and should not be used in production
    environments.
    """
    return API_KEY

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency for flexible date parsing
# ---------------------------------------------------------------------------
try:  # pragma: no cover - the package is optional
    import dateparser as _dateparser  # type: ignore
except Exception:  # pragma: no cover - missing dependency
    _dateparser = None  # type: ignore

# ---------------------------------------------------------------------------
# Pydantic models mirroring the working example
# ---------------------------------------------------------------------------
from pydantic import BaseModel

try:  # pragma: no cover - pydantic v2
    from pydantic import ConfigDict

    class Item(BaseModel):
        descripcion: Optional[str] = None
        cantidad: Optional[float] = None
        unidad: Optional[str] = None
        precio_unitario: Optional[float] = None
        subtotal: Optional[float] = None
        iva_tasa: Optional[int] = None
        iva_monto: Optional[float] = None
        descripcion_adicional: Optional[str] = None

        model_config = ConfigDict(extra="allow")


    class InvoiceOut(BaseModel):
        proveedor: Optional[str] = None
        ruc_proveedor: Optional[str] = None
        timbrado: Optional[str] = None
        numero_comprobante: Optional[str] = None
        fecha: Optional[str] = None
        condicion_venta: Optional[str] = None
        moneda: Optional[str] = None
        subtotal: Optional[float] = None
        iva_10: Optional[float] = None
        iva_5: Optional[float] = None
        total: Optional[float] = None
        items: Optional[List[Item]] = None

        model_config = ConfigDict(extra="allow")

        def apply_defaults_and_validate(self) -> None:
            self.moneda = self.moneda or "PYG"
            self.items = self.items or []
            if self.ruc_proveedor and not re.match(r"^\d{6,8}-[0-9Xx]$", self.ruc_proveedor):
                self.ruc_proveedor = None
            if self.timbrado and not re.match(r"^\d{8}$", self.timbrado):
                self.timbrado = None

except Exception:  # pragma: no cover - pydantic v1 fallback
    class Item(BaseModel):  # type: ignore[no-redef]
        descripcion: Optional[str] = None
        cantidad: Optional[float] = None
        unidad: Optional[str] = None
        precio_unitario: Optional[float] = None
        subtotal: Optional[float] = None
        iva_tasa: Optional[int] = None
        iva_monto: Optional[float] = None
        descripcion_adicional: Optional[str] = None

        class Config:
            extra = "allow"

    class InvoiceOut(BaseModel):  # type: ignore[no-redef]
        proveedor: Optional[str] = None
        ruc_proveedor: Optional[str] = None
        timbrado: Optional[str] = None
        numero_comprobante: Optional[str] = None
        fecha: Optional[str] = None
        condicion_venta: Optional[str] = None
        moneda: Optional[str] = None
        subtotal: Optional[float] = None
        iva_10: Optional[float] = None
        iva_5: Optional[float] = None
        total: Optional[float] = None
        items: Optional[List[Item]] = None

        class Config:
            extra = "allow"

        def apply_defaults_and_validate(self) -> None:
            self.moneda = self.moneda or "PYG"
            self.items = self.items or []
            if self.ruc_proveedor and not re.match(r"^\d{6,8}-[0-9Xx]$", self.ruc_proveedor):
                self.ruc_proveedor = None
            if self.timbrado and not re.match(r"^\d{8}$", self.timbrado):
                self.timbrado = None

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def normalize_date(s: Optional[str]) -> Optional[str]:
    """Normalise ``s`` to ``YYYY-MM-DD`` when possible."""

    if not s:
        return None
    if _dateparser:
        dt = _dateparser.parse(s, languages=["es"])  # pragma: no cover - depends on lib
        try:
            return dt.strftime("%Y-%m-%d") if dt else None
        except Exception:  # pragma: no cover - defensive
            return None
    m = re.search(r"\b([0-3]\d)[/\-.]([0-1]\d)[/\-.]([12]\d{3})\b", s)
    if m:
        try:
            return datetime.strptime(
                f"{m.group(1)}/{m.group(2)}/{m.group(3)}", "%d/%m/%Y"
            ).strftime("%Y-%m-%d")
        except Exception:  # pragma: no cover - defensive
            return None
    return None


def _to_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:  # pragma: no cover - defensive
            logger.debug("No se pudo convertir '%s' a float", value)
    return None


def postprocess_items_fill_iva(inv: InvoiceOut) -> None:
    for it in inv.items:
        if (
            it.iva_monto is None
            and it.subtotal is not None
            and it.iva_tasa in (0, 5, 10)
        ):
            try:
                it.iva_monto = round(it.subtotal * (it.iva_tasa / 100.0), 2)
            except Exception:  # pragma: no cover - defensive
                pass


def _has_fraction(x: Optional[float]) -> bool:
    try:
        return x is not None and float(x) != int(round(float(x)))
    except Exception:  # pragma: no cover - defensive
        return False


def _auto_should_scale_thousands(inv: InvoiceOut) -> bool:
    if (inv.moneda or "PYG").upper() != "PYG":
        return False
    prices = [it.precio_unitario for it in inv.items if it.precio_unitario]
    if not prices:
        return False
    small = [p for p in prices if p < 1000]
    frac = [p for p in prices if p < 1000 and _has_fraction(p)]
    return len(small) >= max(1, int(0.6 * len(prices))) and len(frac) >= max(1, int(0.5 * len(prices)))


def _scale_money_fields(inv: InvoiceOut, factor: float) -> None:
    def s(v: Optional[float]) -> Optional[float]:
        return None if v is None else v * factor

    inv.subtotal = s(inv.subtotal)
    inv.iva_10 = s(inv.iva_10)
    inv.iva_5 = s(inv.iva_5)
    inv.total = s(inv.total)
    for it in inv.items:
        it.precio_unitario = s(it.precio_unitario)
        it.subtotal = s(it.subtotal)
        it.iva_monto = s(it.iva_monto)


def _round_money_fields_to_int(inv: InvoiceOut) -> None:
    def r(v: Optional[float]) -> Optional[int]:
        return None if v is None else int(round(v))

    inv.subtotal = r(inv.subtotal)
    inv.iva_10 = r(inv.iva_10)
    inv.iva_5 = r(inv.iva_5)
    inv.total = r(inv.total)
    for it in inv.items:
        it.precio_unitario = r(it.precio_unitario)
        it.subtotal = r(it.subtotal)
        it.iva_monto = r(it.iva_monto)


def normalize_numbers(
    inv: InvoiceOut, scale_policy: str = "auto", round_to_int: bool = False
) -> None:
    """Normalise monetary fields for PYG.

    ``scale_policy`` accepts ``auto`` (detect thousands), ``x1000`` (force scaling)
    or ``none``.  When ``round_to_int`` is True all monetary fields are rounded to
    integers, matching the example script.  Tests keep ``round_to_int=False`` to
    preserve decimals.
    """

    do_scale = False
    if scale_policy == "x1000":
        do_scale = True
    elif scale_policy == "auto":
        do_scale = _auto_should_scale_thousands(inv)
    if do_scale:
        _scale_money_fields(inv, 1000.0)
    postprocess_items_fill_iva(inv)
    if round_to_int:
        _round_money_fields_to_int(inv)

# ---------------------------------------------------------------------------
# Gemini helpers
# ---------------------------------------------------------------------------
PROMPT = """
Eres un extractor de datos para facturas en español (Paraguay).
Devuelve SOLO JSON válido que cumpla el siguiente esquema. No inventes: si un campo no está, usa null.

Esquema:
{
  "proveedor": str|null,
  "ruc_proveedor": str|null,
  "timbrado": str|null,
  "numero_comprobante": str|null,
  "fecha": str|null,
  "condicion_venta": str|null,
  "moneda": str|null,
  "subtotal": number|null,
  "iva_10": number|null,
  "iva_5": number|null,
  "total": number|null,
  "items": [
    {
      "descripcion": str|null,
      "cantidad": number|null,
      "unidad": str|null,
      "precio_unitario": number|null,
      "subtotal": number|null,
      "iva_tasa": number|null,
      "iva_monto": number|null
    }
  ]|null
}

Reglas:
- No alucines ítems: solo incluye los renglones visibles.
- No incluyas comentarios adicionales, SOLO el JSON.
"""


def _load_image_bytes(path: str) -> tuple[bytes, str]:
    """Return image bytes and mime type, converting to JPEG when possible."""

    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    try:
        from PIL import Image  # pragma: no cover - heavy dependency

        img = Image.open(path).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        with open(path, "rb") as fh:
            return fh.read(), mime


def call_model_once(client: Any, model_name: str, image_path: str) -> InvoiceOut:
    """Call ``model_name`` once and parse the JSON into ``InvoiceOut``."""

    types_mod = getattr(client, "types", getattr(client.__class__, "types", None))
    image_bytes, mime = _load_image_bytes(image_path)
    part_cls = getattr(types_mod, "Part", None) if types_mod else None
    content_cls = getattr(types_mod, "Content", None) if types_mod else None

    part_prompt = (
        part_cls.from_text(PROMPT)
        if part_cls is not None and hasattr(part_cls, "from_text")
        else {"text": PROMPT}
    )
    part_image = (
        part_cls.from_bytes(data=image_bytes, mime_type=mime)
        if part_cls is not None and hasattr(part_cls, "from_bytes")
        else {"inline_data": {"mime_type": mime, "data": image_bytes}}
    )
    content = (
        content_cls(parts=[part_prompt, part_image])
        if content_cls is not None
        else {"parts": [part_prompt, part_image]}
    )

    cfg = None
    types_mod = getattr(client, "types", None)
    if types_mod is not None and hasattr(types_mod, "GenerateContentConfig"):
        cfg = types_mod.GenerateContentConfig(response_mime_type="application/json")
    params: Dict[str, Any] = {
        "model": model_name,
        "contents": [content],
    }
    if cfg is not None:
        params["config"] = cfg

    response = client.models.generate_content(**params)  # type: ignore[attr-defined]
    text = getattr(response, "text", "")
    if not text:
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            content0 = getattr(candidates[0], "content", None)
            parts = getattr(content0, "parts", None) or []
            if parts:
                text = getattr(parts[0], "text", "")
    if not text:
        raise RuntimeError("Gemini no devolvió texto utilizable")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Respuesta JSON malformada del modelo: {text}") from exc

    if isinstance(data, list):
        items_data = data
        rest: Dict[str, Any] = {}
    elif isinstance(data, dict):
        items_data = data.get("items", []) or []
        rest = {k: v for k, v in data.items() if k != "items"}
    else:
        raise ValueError("La respuesta del modelo debe ser una lista o un objeto con 'items'")

    items: List[Item] = []
    for raw in items_data:
        if not isinstance(raw, dict):
            continue
        nombre = (
            raw.get("descripcion")
            or raw.get("producto")
            or raw.get("nombre_producto")
            or raw.get("description")
            or ""
        )
        cantidad = _to_float(raw.get("cantidad"))
        precio_unitario = _to_float(raw.get("precio_unitario"))
        subtotal = _to_float(raw.get("subtotal"))
        precio_fallback = (
            _to_float(raw.get("precio"))
            or _to_float(raw.get("costo_unitario"))
        )
        if precio_unitario is None:
            precio_unitario = precio_fallback
        descripcion = raw.get("descripcion_adicional")
        conocidos = {
            "descripcion",
            "producto",
            "nombre_producto",
            "description",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "precio",
            "costo_unitario",
            "unidad",
            "iva_tasa",
            "iva_monto",
            "descripcion_adicional",
        }
        extras = {k: v for k, v in raw.items() if k not in conocidos}
        if descripcion is None and extras:
            descripcion = ", ".join(f"{k}: {v}" for k, v in extras.items())
        item = Item(
            descripcion=str(nombre) if nombre else None,
            cantidad=cantidad,
            unidad=raw.get("unidad"),
            precio_unitario=precio_unitario,
            subtotal=subtotal,
            iva_tasa=_to_float(raw.get("iva_tasa")),
            iva_monto=_to_float(raw.get("iva_monto")),
            descripcion_adicional=descripcion,
        )
        items.append(item)

    inv = InvoiceOut(items=items, **rest)
    inv.apply_defaults_and_validate()
    inv.fecha = normalize_date(inv.fecha)
    return inv


def extract_invoice_with_fallback(
    path: str, prefer_fast: bool = True
) -> InvoiceOut:
    """Try the fast model first and fall back to the accurate one if needed."""

    try:
        import google.genai as genai  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "Falta el paquete 'google-genai'. Instálalo con `pip install google-genai`."
        ) from exc

    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    primary = "gemini-1.5-flash" if prefer_fast else "gemini-1.5-pro"
    secondary = "gemini-1.5-pro" if prefer_fast else "gemini-1.5-flash"
    try:
        data = call_model_once(client, primary, path)
    except Exception as e:
        logger.warning("Error con %s: %s. Probando %s ...", primary, e, secondary)
        data = call_model_once(client, secondary, path)

    def _poor_detail(d: InvoiceOut) -> bool:
        no_items = (not d.items) or all((i.descripcion is None) for i in d.items)
        weak_totals = (
            d.total is None and d.subtotal is None and (d.iva_10 is None and d.iva_5 is None)
        )
        return no_items and weak_totals

    if _poor_detail(data):
        try:
            logger.info("Detalle insuficiente con %s. Reintentando con %s ...", primary, secondary)
            data = call_model_once(client, secondary, path)
        except Exception as e:
            logger.warning("Fallback %s falló: %s", secondary, e)
    return data


# ---------------------------------------------------------------------------
# Public entry point used by the rest of the project
# ---------------------------------------------------------------------------
def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image and return item dictionaries.

    Only a very small subset of the full invoice is returned since the rest of
    the project only consumes item level information.
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError("Unsupported format: only .jpeg, .jpg or .png images are allowed")

    invoice = extract_invoice_with_fallback(path, prefer_fast=True)
    normalize_numbers(invoice, scale_policy="none", round_to_int=False)

    items: List[Dict] = []
    for it in invoice.items:
        nombre = it.descripcion or ""
        precio = it.precio_unitario
        if precio is None:
            precio = it.subtotal
        item: Dict[str, Any] = {
            "producto": nombre,
            "cantidad": float(it.cantidad or 0.0),
        }
        if precio is not None:
            item["precio"] = float(precio)
        if it.descripcion_adicional:
            item["descripcion_adicional"] = it.descripcion_adicional
        items.append(item)

    return items
