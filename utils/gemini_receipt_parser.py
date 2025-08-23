# gemini_receipt_parser.py
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

# Optional dependencies
try:
    import dateparser as _dateparser
except ImportError:
    _dateparser = None

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    Image = None
    UnidentifiedImageError = Exception  # type: ignore

try:
    from fuzzywuzzy import fuzz
except ImportError:
    fuzz = None

# Pydantic models (unchanged)
from pydantic import BaseModel

try:
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
        ruc_proveedor: Optional[str] = None
        timbrado: Optional[str] = None
        ruc: Optional[str] = None
        numero: Optional[str] = None
        fecha: Optional[str] = None
        total: Optional[float] = None
        extras: Dict[str, Any] = {}

        model_config = ConfigDict(extra="allow")

        def apply_defaults_and_validate(self) -> None:
            self.items = self.items or []

except Exception:
    class Item(BaseModel):
        descripcion: Optional[str] = None
        cantidad: Optional[float] = None
        precio_unitario: Optional[float] = None
        subtotal: Optional[float] = None
        producto: Optional[str] = None
        precio: Optional[float] = None
        descripcion_adicional: Optional[str] = None

        class Config:
            extra = "allow"

    class InvoiceOut(BaseModel):
        items: List[Item] = []
        proveedor: Optional[str] = None
        ruc_proveedor: Optional[str] = None
        timbrado: Optional[str] = None
        ruc: Optional[str] = None
        numero: Optional[str] = None
        fecha: Optional[str] = None
        total: Optional[float] = None
        extras: Dict[str, Any] = {}

        class Config:
            extra = "allow"

        def apply_defaults_and_validate(self) -> None:
            self.items = self.items or []

# Helper functions (unchanged)
def normalize_date(value: Optional[str]) -> Optional[str]:
    """Normalise `value` to `YYYY-MM-DD` when possible."""
    if not value:
        return None
    if _dateparser:
        dt = _dateparser.parse(value, languages=["es"])
        if dt:
            try:
                return dt.strftime("%Y-%m-%d")
            except Exception:
                return None
    m = re.search(r"\b([0-3]\d)[/\-.]([0-1]\d)[/\-.]([12]\d{3})\b", value)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(1)}/{m.group(2)}/{m.group(3)}", "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
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
        except ValueError:
            logger.debug("No se pudo convertir '%s' a float", value)
    return None

def _has_fraction(x: Optional[float]) -> bool:
    try:
        return x is not None and float(x) != int(round(float(x)))
    except Exception:
        return False

def _auto_should_scale_thousands(inv: InvoiceOut) -> bool:
    prices: List[float] = []
    for it in inv.items:
        for p in [it.precio, it.precio_unitario, it.subtotal]:
            if p and p > 0:
                prices.append(p)
                break
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
        it.precio_unitario = s(it.precio_unitario)
        it.subtotal = s(it.subtotal)

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

# New function to load and match materials
def load_materias_primas(file_path: str = r"C:\Users\ASUS\OneDrive - ITAIPU Binacional\Personal\Cafe\data\materias_primas.json") -> List[Dict]:
    """Load materias primas from JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("No se encontró el archivo %s", file_path)
        return []
    except json.JSONDecodeError as e:
        logger.error("Error al parsear %s: %s", file_path, e)
        return []

def match_material(producto: str, materias_primas: List[Dict], threshold: int = 80) -> Optional[Dict]:
    """Match a producto to a material in materias_primas using fuzzy matching or exact match."""
    if not producto:
        return None
    producto = producto.lower().strip()
    if fuzz:
        best_match = None
        best_score = 0
        for material in materias_primas:
            nombre = material.get("nombre", "").lower().strip()
            score = fuzz.ratio(producto, nombre)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = material
        return best_match
    else:
        # Fallback to simple substring match
        for material in materias_primas:
            nombre = material.get("nombre", "").lower().strip()
            if producto in nombre or nombre in producto:
                return material
        return None

# Image preprocessing
def image_to_part(path: str) -> Any:
    """Convert image to Part, using Pillow if available."""
    try:
        from google.genai.types import Part
    except ImportError as exc:
        raise ImportError(
            "Falta el paquete 'google-generativeai'. Instálalo con `pip install google-generativeai`."
        ) from exc

    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    if Image:
        try:
            img = Image.open(path).convert("RGB")
        except UnidentifiedImageError:
            with io.open(path, "rb") as fh:
                return Part.from_bytes(data=fh.read(), mime_type=mime)
        buf = io.BytesIO()
        img.save(buf, format="JPEG" if mime == "image/jpeg" else "PNG", quality=95)
        buf.seek(0)
        return Part.from_bytes(data=buf.getvalue(), mime_type=mime)
    else:
        with io.open(path, "rb") as fh:
            return Part.from_bytes(data=fh.read(), mime_type=mime)

# Gemini helpers
def call_model_once(model_name: str, image_path: str, content: List, api_key: str) -> InvoiceOut:
    """Invoke model once and parse the resulting `InvoiceOut`."""
    try:
        from google import genai
        from google.genai.types import Content, Part
    except ImportError as exc:
        raise ImportError(
            "Falta el paquete 'google-generativeai'. Instálalo con `pip install google-generativeai`."
        ) from exc

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=[Content(parts=content)],
        config={"response_mime_type": "application/json"}
    )
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

    inv = InvoiceOut(
        items=items,
        **{
            k: rest.get(k)
            for k in [
                "proveedor",
                "ruc_proveedor",
                "timbrado",
                "ruc",
                "numero",
                "fecha",
                "total",
            ]
        },
    )
    extra_keys = set(rest) - {
        "proveedor",
        "ruc_proveedor",
        "timbrado",
        "ruc",
        "numero",
        "fecha",
        "total",
    }
    if extra_keys:
        inv.extras = {k: rest[k] for k in extra_keys}
    inv.apply_defaults_and_validate()
    return inv

def extract_invoice_with_fallback(
    content: List, image_path: str, primary: str, fallback: Optional[str], api_key: str
) -> InvoiceOut:
    """Try `primary` model first and fall back to `fallback` if needed."""
    def _poor_detail(d: InvoiceOut) -> bool:
        no_items = not d.items or all((not it.producto) for it in d.items)
        weak_totals = d.total is None
        return no_items or weak_totals

    try:
        return call_model_once(primary, image_path, content, api_key)
    except Exception as exc:
        logger.warning("Modelo %s falló: %s", primary, exc)
        if not fallback:
            raise
        return call_model_once(fallback, image_path, content, api_key)

    data = call_model_once(primary, image_path, content, api_key)
    if _poor_detail(data) and fallback:
        try:
            logger.info("Resultado insuficiente con %s, intentando %s", primary, fallback)
            return call_model_once(fallback, image_path, content, api_key)
        except Exception as exc:
            logger.warning("Fallback %s falló: %s", fallback, exc)
    return data

def parse_receipt_image(path: str) -> Dict[str, Any]:
    """Parse a receipt image using the Gemini backend.

    Returns a dictionary containing a normalised ``items`` list and metadata
    extracted from the invoice such as ``proveedor``, ``fecha`` and ``total``.
    """
    try:
        from google import genai
        from google.genai.types import Part
    except ImportError as exc:
        raise ImportError(
            "Falta el paquete 'google-generativeai'. Instálalo con `pip install google-generativeai`."
        ) from exc

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError("Unsupported format: only .jpeg, .jpg or .png images are allowed")

    api_key = get_gemini_api_key()
    content = [
        Part.from_text(text="""
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
                  "producto": str|null,
                  "cantidad": number|null,
                  "precio": number|null,
                  "descripcion_adicional": str|null
                }
              ]|null
            }
        """),
        image_to_part(path)
    ]

    model_flash = "gemini-1.5-flash"
    model_pro = "gemini-1.5-pro"

    invoice = extract_invoice_with_fallback(content, path, model_flash, model_pro, api_key)
    invoice = normalize_numbers(invoice)

    # Load materias primas
    materias_primas = load_materias_primas()

    # Autocomplete fields
    items: List[Dict] = []
    for it in invoice.items:
        nombre = it.producto or ""
        precio = it.precio or 0.0
        cantidad = float(it.cantidad or 0.0)
        item: Dict[str, Any] = {
            "producto": nombre,
            "cantidad": cantidad,
            "precio": float(precio),
        }
        if it.descripcion_adicional:
            item["descripcion_adicional"] = it.descripcion_adicional

        # Match with materias primas
        matched_material = match_material(nombre, materias_primas)
        if matched_material:
            item["unidad_medida"] = matched_material.get("unidad_medida", None)
            item["costo_unitario"] = matched_material.get("costo_unitario", precio)
            item["stock"] = matched_material.get("stock", 0.0) + cantidad
        else:
            item["unidad_medida"] = None
            item["costo_unitario"] = precio  # Fallback to receipt price
            item["stock"] = cantidad  # Assume new stock is the purchased quantity

        items.append(item)

    # Build output with items and relevant metadata
    result: Dict[str, Any] = {
        "items": items,
        "proveedor": invoice.proveedor,
        "ruc_proveedor": invoice.ruc_proveedor,
        "timbrado": invoice.timbrado,
        "ruc": invoice.ruc,
        "numero": invoice.numero,
        "fecha": invoice.fecha,
        "total": invoice.total,
    }
    if invoice.extras:
        result["extras"] = invoice.extras

    return result