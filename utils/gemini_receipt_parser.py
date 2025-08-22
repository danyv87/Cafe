"""Receipt parser powered by the Gemini API.

This module communicates with Google's Gemini models to extract structured
data from receipt images. It relies on the external ``google-genai`` package
and the :func:`utils.gemini_api.get_gemini_api_key` helper to obtain the
authentication token from a safe location.
"""

from __future__ import annotations

import os
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .gemini_api import get_gemini_api_key

logger = logging.getLogger(__name__)


@dataclass
class Item:
    """Representa un producto detectado en la factura."""

    producto: str
    cantidad: Any
    precio: Any
    descripcion_adicional: Optional[str] = None


@dataclass
class InvoiceOut:
    """Estructura de salida de la factura devuelta por Gemini."""

    items: List[Item] = field(default_factory=list)
    proveedor: Optional[str] = None
    ruc: Optional[str] = None
    numero: Optional[str] = None
    fecha: Optional[str] = None
    total: Any = None
    extras: Dict[str, Any] = field(default_factory=dict)


def normalize_numbers(inv: InvoiceOut) -> InvoiceOut:
    """Normaliza números y fechas presentes en ``inv``."""

    def _to_float(value: Any) -> float:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace(".", "").replace(",", ".")
            try:
                return float(cleaned)
            except ValueError:
                logger.debug("No se pudo convertir '%s' a float", value)
        return 0.0

    for it in inv.items:
        it.cantidad = _to_float(it.cantidad)
        it.precio = _to_float(it.precio)

    if inv.total is not None:
        inv.total = _to_float(inv.total)

    if inv.fecha:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                inv.fecha = datetime.strptime(inv.fecha, fmt).date().isoformat()
                break
            except Exception:
                continue

    return inv


def call_model_once(client: Any, model: str, content: Any) -> InvoiceOut:
    """Realiza una única llamada al modelo y devuelve ``InvoiceOut``."""

    try:
        import google.genai as genai  # type: ignore[import]
    except Exception:
        genai = None  # type: ignore[assignment]

    params: Dict[str, Any] = {"model": model, "contents": [content]}

    # Compatibilidad con distintos releases de google-genai
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
        item = Item(
            producto=str(raw.get("producto", "")),
            cantidad=raw.get("cantidad", 0),
            precio=raw.get("precio", 0),
            descripcion_adicional=raw.get("descripcion_adicional"),
        )
        items.append(item)

    inv = InvoiceOut(items=items, **{k: rest.get(k) for k in ["proveedor", "ruc", "numero", "fecha", "total"]})
    extra_keys = set(rest) - {"proveedor", "ruc", "numero", "fecha", "total"}
    if extra_keys:
        inv.extras = {k: rest[k] for k in extra_keys}
    return inv


def extract_invoice_with_fallback(
    client: Any, content: Any, primary: str, fallback: Optional[str] = None
) -> InvoiceOut:
    """Intenta extraer la factura usando ``primary`` y recurre a ``fallback``."""

    try:
        return call_model_once(client, primary, content)
    except Exception as exc:
        logger.warning("Modelo %s falló: %s", primary, exc)
        if not fallback:
            raise
        try:
            return call_model_once(client, fallback, content)
        except Exception as exc2:
            if isinstance(exc2, ValueError):
                raise exc2
            raise RuntimeError(
                f"Fallo al invocar los modelos {primary} y {fallback}: {exc2}"
            ) from exc2


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image using the Gemini backend.

    Parameters
    ----------
    path: str
        Path to an image (``.jpeg``, ``.jpg`` or ``.png``) containing the
        receipt.

    Returns
    -------
    list of dict
        A list of dictionaries describing the items found in the receipt.
    """
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
    with open(path, "rb") as fh:
        image_bytes = fh.read()

    prompt = (
        "Extrae todos los productos del comprobante y devuelve un JSON con una "
        "lista de objetos. Cada objeto debe contener las claves 'producto', "
        "'cantidad', 'precio' y opcionalmente 'descripcion_adicional'."
    )

    # Construye el contenido usando tipos nativos si están disponibles
    types_mod = getattr(genai, "types", None)
    part_cls = getattr(types_mod, "Part", None) if types_mod else None
    content_cls = getattr(types_mod, "Content", None) if types_mod else None

    # Handle part_text construction
    if part_cls is not None and hasattr(part_cls, "from_text"):
        try:
            # Attempt to call from_text as a static method
            part_text = part_cls.from_text(text=prompt)
        except TypeError as e:
            logger.error("Error calling Part.from_text: %s", e)
            # Fallback to dictionary structure if from_text fails
            part_text = {"text": prompt}
    else:
        part_text = {"text": prompt}

    # Handle part_image construction
    if part_cls is not None and hasattr(part_cls, "from_bytes"):
        try:
            part_image = part_cls.from_bytes(data=image_bytes, mime_type=mime)
        except TypeError as e:
            logger.error("Error calling Part.from_bytes: %s", e)
            part_image = {"inline_data": {"mime_type": mime, "data": image_bytes}}
    else:
        part_image = {"inline_data": {"mime_type": mime, "data": image_bytes}}

    # Construct content
    if content_cls is not None:
        content = content_cls(role="user", parts=[part_text, part_image])
    else:
        content = {"role": "user", "parts": [part_text, part_image]}

    try:
        invoice = extract_invoice_with_fallback(
            client, content, "gemini-1.5-flash", "gemini-1.5-pro"
        )
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Error al comunicarse con el servicio Gemini: {exc}") from exc

    invoice = normalize_numbers(invoice)

    items: List[Dict] = []
    for it in invoice.items:
        item = {
            "producto": it.producto,
            "cantidad": float(it.cantidad),
            "precio": float(it.precio),
        }
        if it.descripcion_adicional:
            item["descripcion_adicional"] = it.descripcion_adicional
        items.append(item)

    return items
