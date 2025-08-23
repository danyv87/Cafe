from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List

try:
    from google import genai
except Exception:  # pragma: no cover - library may be absent in tests
    genai = None  # type: ignore

from PIL import Image

API_KEY = "AIzaSyBS-RvRzXXhnm2rdPKgtpmUy_CIBTIp63o"
MODEL_NAME = "gemini-1.5-flash"

# Initialize client if library is available.  Tests may patch this client
# directly, so we expose it as a module level attribute.
client = genai.Client(api_key=API_KEY) if genai else None

def _normalize_date(date_str: str) -> str:
    """Return ``date_str`` normalized to ``YYYY-MM-DD`` if possible."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return date_str

def _parse_iva(value: Any) -> float:
    """Return numeric IVA percentage from ``value`` (e.g. ``"21%"`` -> ``21``)."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"\d+(?:\.\d+)?", value)
        if match:
            return float(match.group())
    return 0.0

def _prepare_item(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw item extracted by Gemini."""
    cantidad = float(raw.get("cantidad", 0))
    costo = float(raw.get("costo_unitario") or raw.get("precio", 0))
    iva = _parse_iva(raw.get("iva"))
    total = raw.get("total")
    if total is None:
        total = round(cantidad * costo * (1 + iva / 100), 2)
    nombre = (
        raw.get("nombre_producto")
        or raw.get("descripcion")
        or raw.get("item")
        or ""
    )
    return {
        "nombre_producto": nombre,
        "cantidad": cantidad,
        "costo_unitario": costo,
        "iva": iva,
        "total": total,
    }

def parse_invoice(image_path: str) -> Dict[str, Any]:
    """Use Gemini to extract structured data from an invoice image.

    Parameters
    ----------
    image_path:
        Path to the invoice image file.

    Returns
    -------
    dict
        Dictionary with keys ``proveedor``, ``fecha`` (``YYYY-MM-DD``) and
        ``items`` (list of dictionaries with ``nombre_producto``, ``cantidad``,
        ``costo_unitario``, ``iva`` and ``total``).
    """
    if client is None:  # pragma: no cover - handled in tests
        raise RuntimeError("google.genai is not available")

    with Image.open(image_path) as img:
        prompt = (
            "Extrae los datos de la factura y devuelve un JSON con las claves "
            "'proveedor', 'fecha' e 'items' (lista de objetos con 'nombre_producto', "
            "'cantidad', 'costo_unitario' e 'iva')."
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, img],
        )

    # The response from the Gemini client is expected to expose a ``text``
    # attribute containing the model output.  Tests may stub this behaviour.
    text = getattr(response, "text", "")
    if not text and getattr(response, "candidates", None):
        # Fallback to first candidate's text field
        try:
            text = response.candidates[0].content[0].text
        except Exception:  # pragma: no cover - best effort
            text = ""

    data = json.loads(text) if text else {}
    fecha = _normalize_date(data.get("fecha", ""))
    items = [_prepare_item(item) for item in data.get("items", [])]
    return {"proveedor": data.get("proveedor", ""), "fecha": fecha, "items": items}

__all__ = ["parse_invoice", "client", "API_KEY"]
