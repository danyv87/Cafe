"""Gemini based receipt parser.

This module mirrors the behaviour of ``testfactura.py`` while using Google's
Gemini models to extract structured data from receipt images. The API key is
retrieved via :func:`utils.gemini_api.get_gemini_api_key` and the results are
normalised for the application.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from .gemini_api import get_gemini_api_key

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency for flexible date parsing
# ---------------------------------------------------------------------------
try:  # pragma: no cover - the package is optional
    import dateparser as _dateparser  # type: ignore
except Exception:  # pragma: no cover - missing dependency
    _dateparser = None  # type: ignore

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
from pydantic import BaseModel

try:  # pydantic v2
    from pydantic import ConfigDict

    class Item(BaseModel):
        """Representa un producto detectado en la factura."""

        descripcion: Optional[str] = None
        cantidad: Optional[float] = None
        precio_unitario: Optional[float] = None
        subtotal: Optional[float] = None
        producto: Optional[str] = None
        precio: Optional[float] = None
        descripcion_adicional: Optional[str] = None

        model_config = ConfigDict(extra="allow")


    class InvoiceOut(BaseModel):
        """Estructura de salida del comprobante."""

        items: List[Item] = []
        proveedor: Optional[str] = None
        ruc: Optional[str] = None
        numero: Optional[str] = None
        fecha: Optional[str] = None
        total: Optional[float] = None
        extras: Dict[str, Any] = {}

        model_config = ConfigDict(extra="allow")

        def apply_defaults_and_validate(self) -> None:
            self.items = self.items or []

except Exception:  # pragma: no cover - pydantic v1 fallback
    class Item(BaseModel):  # type: ignore[no-redef]
        descripcion: Optional[str] = None
        cantidad: Optional[float] = None
        precio_unitario: Optional[float] = None
        subtotal: Optional[float] = None
        producto: Optional[str] = None
        precio: Optional[float] = None
        descripcion_adicional: Optional[str] = None

        class Config:
            extra = "allow"

    class InvoiceOut(BaseModel):  # type: ignore[no-redef]
        items: List[Item] = []
        proveedor: Optional[str] = None
        ruc: Optional[str] = None
        numero: Optional[str] = None
        fecha: Optional[str] = None
        total: Optional[float] = None
        extras: Dict[str, Any] = {}

        class Config:
            extra = "allow"

        def apply_defaults_and_validate(self) -> None:
            self.items = self.items or []


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def normalize_date(value: Optional[str]) -> Optional[str]:
    """Normalise ``value`` to ``YYYY-MM-DD`` when possible."""

    if not value:
        return None
    if _dateparser:
        dt = _dateparser.parse(value, languages=["es"])  # pragma: no cover - depends on lib
        if dt:
            try:
                return dt.strftime("%Y-%m-%d")
            except Exception:  # pragma: no cover - defensive
                return None
    m = re.search(r"\b([0-3]\d)[/\-.]([0-1]\d)[/\-.]([12]\d{3})\b", value)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(1)}/{m.group(2)}/{m.group(3)}", "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
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


def _has_fraction(x: Optional[float]) -> bool:
    try:
        return x is not None and float(x) != int(round(float(x)))
    except Exception:  # pragma: no cover - defensive
        return False


def _auto_should_scale_thousands(inv: InvoiceOut) -> bool:
    prices = [it.precio for it in inv.items if it.precio and it.precio > 0]
    if len(prices) < 2:
        return False
    small = [p for p in prices if p < 1000]
    frac = [p for p in prices if p < 1000 and _has_fraction(p)]
    return len(small) >= max(1, int(0.6 * len(prices))) and len(frac) >= max(1, int(0.5 * len(prices)))


def _scale_money_fields(inv: InvoiceOut, factor: float) -> None:
    def s(v: Optional[float]) -> Optional[float]:
        return None if v is None else v * factor

    inv.total = s(inv.total)
    for it in inv.items:
        it.precio = s(it.precio)


def normalize_numbers(inv: InvoiceOut, scale_policy: str = "auto") -> InvoiceOut:
    """Normalise numeric fields and optionally scale to thousands."""

    for it in inv.items:
        it.cantidad = _to_float(it.cantidad) or 0.0
        it.precio = _to_float(it.precio)
        it.precio_unitario = _to_float(it.precio_unitario)
        it.subtotal = _to_float(it.subtotal)

    inv.total = _to_float(inv.total)
    inv.fecha = normalize_date(inv.fecha)

    do_scale = False
    if scale_policy == "x1000":
        do_scale = True
    elif scale_policy == "auto":
        do_scale = _auto_should_scale_thousands(inv)
    if do_scale:
        _scale_money_fields(inv, 1000.0)

    return inv


# ---------------------------------------------------------------------------
# Gemini helpers
# ---------------------------------------------------------------------------
def call_model_once(client: Any, model: str, content: Any) -> InvoiceOut:
    """Invoke ``model`` once and parse the resulting ``InvoiceOut``."""

    try:
        import google.genai as genai  # type: ignore[import]
    except Exception:  # pragma: no cover - the dependency is mandatory
        genai = None  # type: ignore[assignment]

    params: Dict[str, Any] = {"model": model, "contents": [content]}
    types_mod = getattr(genai, "types", None) if genai else None
    if types_mod is not None:
        gen_config = (
            getattr(types_mod, "GenerateContentConfig")(response_mime_type="application/json")
            if hasattr(types_mod, "GenerateContentConfig")
            else getattr(types_mod, "GenerationConfig")(response_mime_type="application/json")
        )
        generate_content_fn = client.models.generate_content  # type: ignore[attr-defined]
        if "config" in getattr(generate_content_fn.__code__, "co_varnames", ()):
            params["config"] = gen_config
        else:  # API antigua
            params["generation_config"] = gen_config

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
        items_data = data.get("items", [])
        rest = {k: v for k, v in data.items() if k != "items"}
    else:
        raise ValueError("La respuesta del modelo debe ser una lista o un objeto con 'items'")

    items: List[Item] = []
    for raw in items_data:
        if not isinstance(raw, dict):
            continue
        nombre = (
            raw.get("producto")
            or raw.get("nombre_producto")
            or raw.get("descripcion")
            or raw.get("description")
            or ""
        )
        cantidad = raw.get("cantidad")
        precio_unit = raw.get("precio_unitario")
        if precio_unit in (None, ""):
            precio_unit = raw.get("precio")
        if precio_unit in (None, ""):
            precio_unit = raw.get("costo_unitario")
        subtotal = raw.get("subtotal")
        precio = precio_unit if precio_unit not in (None, "") else subtotal
        descripcion = raw.get("descripcion_adicional")
        conocidos = {
            "producto",
            "nombre_producto",
            "descripcion",
            "description",
            "cantidad",
            "precio",
            "costo_unitario",
            "precio_unitario",
            "subtotal",
            "descripcion_adicional",
        }
        extras = {k: v for k, v in raw.items() if k not in conocidos}
        if descripcion is None and extras:
            descripcion = ", ".join(f"{k}: {v}" for k, v in extras.items())
        item = Item(
            descripcion=str(nombre),
            cantidad=cantidad,
            precio_unitario=precio_unit,
            subtotal=subtotal,
            producto=str(nombre),
            precio=precio,
            descripcion_adicional=descripcion,
        )
        items.append(item)

    inv = InvoiceOut(items=items, **{k: rest.get(k) for k in ["proveedor", "ruc", "numero", "fecha", "total"]})
    extra_keys = set(rest) - {"proveedor", "ruc", "numero", "fecha", "total"}
    if extra_keys:
        inv.extras = {k: rest[k] for k in extra_keys}
    inv.apply_defaults_and_validate()
    return inv


def extract_invoice_with_fallback(
    client: Any, content: Any, primary: str, fallback: Optional[str] = None
) -> InvoiceOut:
    """Try ``primary`` model first and fall back to ``fallback`` if needed."""

    def _poor_detail(d: InvoiceOut) -> bool:
        no_items = not d.items or all((not it.producto) for it in d.items)
        return no_items

    try:
        data = call_model_once(client, primary, content)
    except Exception as exc:
        logger.warning("Modelo %s falló: %s", primary, exc)
        if not fallback:
            raise
        return call_model_once(client, fallback, content)

    if _poor_detail(data) and fallback:
        try:
            return call_model_once(client, fallback, content)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Fallback %s falló: %s", fallback, exc)
    return data


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image using the Gemini backend."""

    try:
        import google.genai as genai  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "Falta el paquete 'google-genai'. Instálalo con `pip install google-genai`."
        ) from exc

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError("Unsupported format: only .jpeg, .jpg or .png images are allowed")

    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    with io.open(path, "rb") as fh:
        image_bytes = fh.read()

    prompt = (
        "Extrae todos los productos del comprobante y devuelve un JSON con una "
        "lista de objetos. Cada objeto debe contener las claves 'producto', "
        "'cantidad', 'precio' y opcionalmente 'descripcion_adicional'."
    )

    types_mod = getattr(genai, "types", None)
    part_cls = getattr(types_mod, "Part", None) if types_mod else None
    content_cls = getattr(types_mod, "Content", None) if types_mod else None

    part_text = (
        part_cls.from_text(text=prompt)
        if part_cls is not None and hasattr(part_cls, "from_text")
        else {"text": prompt}
    )
    part_image = (
        part_cls.from_bytes(data=image_bytes, mime_type=mime)
        if part_cls is not None and hasattr(part_cls, "from_bytes")
        else {"inline_data": {"mime_type": mime, "data": image_bytes}}
    )
    content = (
        content_cls(role="user", parts=[part_text, part_image])
        if content_cls is not None
        else {"role": "user", "parts": [part_text, part_image]}
    )

    invoice = extract_invoice_with_fallback(
        client, content, "gemini-1.5-flash", "gemini-1.5-pro"
    )
    invoice = normalize_numbers(invoice)

    items: List[Dict] = []
    for it in invoice.items:
        nombre = it.producto or ""
        precio = it.precio or 0.0
        item: Dict[str, Any] = {
            "producto": nombre,
            "cantidad": float(it.cantidad or 0.0),
            "precio": float(precio),
        }
        if it.descripcion_adicional:
            item["descripcion_adicional"] = it.descripcion_adicional
        items.append(item)

    return items

