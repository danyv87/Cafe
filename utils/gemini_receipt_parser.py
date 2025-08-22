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
        if "config" in genai.Client.models.generate_content.__code__.co_varnames:
            params["config"] = gen_config
        else:  # pragma: no cover - legacy API
            params["generation_config"] = gen_config

        response = client.models.generate_content(**params)  # type: ignore[attr-defined]
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
        required = {"producto", "cantidad", "precio"}
        if not required.issubset(raw_item):
            raise ValueError(
                "Cada elemento debe contener 'producto', 'cantidad' y 'precio'"
            )
        producto = str(raw_item["producto"])
        try:
            cantidad = float(raw_item["cantidad"])
            precio = float(raw_item["precio"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Los campos 'cantidad' y 'precio' deben ser numéricos"
            ) from exc
        item = {"producto": producto, "cantidad": cantidad, "precio": precio}
        if "descripcion_adicional" in raw_item:
            item["descripcion_adicional"] = str(raw_item["descripcion_adicional"])
        items.append(item)

    return items
