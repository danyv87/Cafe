"""Receipt parser powered by the Gemini API.

This module communicates with Google's Gemini models to extract structured
data from receipt images.  It relies on the external ``google-genai`` package
and the :func:`utils.gemini_api.get_gemini_api_key` helper to obtain the
authentication token from a safe location.
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, List

from .gemini_api import get_gemini_api_key

logger = logging.getLogger(__name__)


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

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist.
    ValueError
        If the extension is not one of the supported formats.
    ImportError
        If the ``google-genai`` dependency is missing.
    ValueError
        If the model returns data that is not valid JSON or does not match the
        expected structure.
    RuntimeError
        For errors raised by the remote service or network issues.
    """

    try:
        import google.genai as genai  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError(
            "Falta el paquete 'google-genai'. Instálalo con `pip install google-genai`."
        ) from exc

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError("Unsupported format: only .jpeg, .jpg or .png images are allowed")

    # Retrieve the API key without exposing secrets directly in the code
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

    try:
        # ``GenerateContentConfig`` is available in newer versions of
        # ``google-genai``.  Older releases exposed ``GenerationConfig`` and
        # accepted it via the ``generation_config`` parameter.  Build the
        # appropriate configuration object and pass it using the correct
        # keyword for maximum compatibility.
        gen_config = (
            genai.types.GenerateContentConfig(
                response_mime_type="application/json"
            )
            if hasattr(genai.types, "GenerateContentConfig")
            else genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        params = {
            "model": "gemini-1.5-flash",
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime, "data": image_bytes}},
                    ],
                }
            ],
        }
        generate_content_fn = client.models.generate_content  # type: ignore[attr-defined]
        if "config" in generate_content_fn.__code__.co_varnames:
            params["config"] = gen_config
        else:  # pragma: no cover - legacy API
            params["generation_config"] = gen_config
        response = generate_content_fn(**params)  # type: ignore[arg-type]
    except Exception as exc:  # pragma: no cover - depends on network/service
        raise RuntimeError(
            f"Error al comunicarse con el servicio Gemini: {exc}"
        ) from exc

    text = getattr(response, "text", "")
    if not text:
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None) or []
            if parts:
                text = getattr(parts[0], "text", "")
    if not text:
        logger.error("Gemini no devolvió texto utilizable: %s", response)
        raise RuntimeError("Gemini no devolvió texto utilizable")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Respuesta JSON malformada del modelo: {text}"
        ) from exc

    if not isinstance(payload, list):
        raise ValueError("La respuesta del modelo debe ser una lista de objetos")

    items: List[Dict] = []
    for raw_item in payload:
        if not isinstance(raw_item, dict):
            raise ValueError(
                "La respuesta del modelo debe ser una lista de diccionarios"
            )

        # Nombre del producto: aceptar variantes comunes como ``descripcion``.
        nombre = (
            raw_item.get("producto")
            or raw_item.get("nombre_producto")
            or raw_item.get("descripcion")
            or raw_item.get("description")
        )
        if not nombre:
            raise ValueError(
                "Cada elemento debe contener 'producto' o 'descripcion'"
            )

        # Cantidad es obligatoria y debe ser numérica.
        if "cantidad" not in raw_item:
            raise ValueError("Cada elemento debe contener 'cantidad'")
        try:
            cantidad = float(raw_item["cantidad"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Los campos 'cantidad' y 'precio' deben ser numéricos"
            ) from exc

        # Determinar el precio preferentemente desde ``precio_unitario``.
        precio_valor = raw_item.get("precio_unitario")
        if precio_valor in (None, ""):
            precio_valor = raw_item.get("costo_unitario")
        if precio_valor in (None, ""):
            precio_valor = raw_item.get("precio")
        if precio_valor in (None, ""):
            precio_valor = raw_item.get("subtotal")
        if precio_valor in (None, ""):
            raise ValueError(
                "Cada elemento debe contener 'precio', 'precio_unitario' o 'subtotal'"
            )
        try:
            precio = float(precio_valor)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Los campos 'cantidad' y 'precio' deben ser numéricos"
            ) from exc

        item = {"producto": str(nombre), "cantidad": cantidad, "precio": precio}

        # Mapear cualquier campo extra a ``descripcion_adicional``.
        descripcion = raw_item.get("descripcion_adicional")
        if descripcion is None:
            extras = {
                k: v
                for k, v in raw_item.items()
                if k
                not in {
                    "producto",
                    "nombre_producto",
                    "descripcion",
                    "description",
                    "cantidad",
                    "precio",
                    "precio_unitario",
                    "costo_unitario",
                    "subtotal",
                    "descripcion_adicional",
                }
            }
            if extras:
                descripcion = ", ".join(f"{k}: {v}" for k, v in extras.items())
        if descripcion:
            item["descripcion_adicional"] = str(descripcion)

        items.append(item)

    return items
