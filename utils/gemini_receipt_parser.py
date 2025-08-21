"""Receipt parser powered by the Gemini API.

This module provides a thin wrapper around the Gemini client so tests can mock
the behaviour of the external service.  The real API is not available in the
execution environment, therefore :func:`parse_receipt_image` is designed to be
easily monkeypatched.
"""

from __future__ import annotations

import json
import mimetypes
import os
from typing import Dict, List

from .gemini_api import get_gemini_api_key


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image using the Gemini backend.

    The function sends ``path`` to the Gemini API and expects a JSON array of
    objects describing the purchased items.  Each object must include the keys
    ``description`` (name of the product), ``quantity`` and ``price``.  The data
    is converted to the application's schema with ``nombre_producto``,
    ``cantidad`` and ``costo_unitario`` keys.

    Parameters
    ----------
    path: str
        Path to an image (``.jpeg``, ``.jpg`` or ``.png``) containing the
        receipt.

    Returns
    -------
    list of dict
        List of item dictionaries in the application's schema.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the Gemini response cannot be decoded or does not follow the
        expected structure.
    NotImplementedError
        If the ``google.genai`` module is not available.
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError(
            "Unsupported format: only .jpeg, .jpg or .png images are allowed",
        )

    try:  # Import lazily so tests can monkeypatch ``google.genai``
        from google import genai  # type: ignore
    except Exception as exc:  # pragma: no cover - library not installed
        raise NotImplementedError(
            "El backend de Gemini para analizar comprobantes no está disponible",
        ) from exc

    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime_type or "image/png"
    with open(path, "rb") as fh:
        img_bytes = fh.read()

    response = client.responses.generate(
        model="gemini-1.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [{"mime_type": mime_type, "data": img_bytes}],
            }
        ],
        output_mime_type="application/json",
    )

    try:
        raw_data = json.loads(getattr(response, "output_text", ""))
    except Exception as exc:  # pragma: no cover - malformed JSON
        raise ValueError("La respuesta del backend de recibos es inválida") from exc

    if not isinstance(raw_data, list):
        raise ValueError("La respuesta del backend de recibos es inválida")

    items: List[Dict] = []
    for entry in raw_data:
        try:
            nombre = entry["description"]
            cantidad = float(entry["quantity"])
            precio = float(entry["price"])
        except Exception as exc:  # pragma: no cover - invalid item structure
            raise ValueError(
                "Datos de item inválidos en la respuesta del backend",
            ) from exc

        items.append(
            {
                "nombre_producto": nombre,
                "cantidad": cantidad,
                "costo_unitario": precio,
                "descripcion_adicional": entry.get("descripcion_adicional", ""),
            }
        )

    return items

