"""Receipt parser powered by the Gemini API.

This module integrates with Google's `gemini` models to obtain structured
information from images of purchase receipts.  It relies on the
``GEMINI_API_KEY`` environment variable (or the encrypted configuration file
used by :func:`utils.gemini_api.get_gemini_api_key`) to authenticate
requests.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

from .gemini_api import get_gemini_api_key


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image using the Gemini backend.

    The function uploads the image to the Gemini API and requests a JSON
    response describing the items present.  The API key must be provided via
    the ``GEMINI_API_KEY`` environment variable or through the encrypted
    configuration file handled by :func:`utils.gemini_api.get_gemini_api_key`.

    Parameters
    ----------
    path: str
        Path to an image (``.jpeg``, ``.jpg`` or ``.png``) containing the
        receipt.

    Returns
    -------
    list of dict
        A list of dictionaries with ``producto``, ``cantidad`` and ``precio``
        keys describing the items found in the receipt.

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist.
    ValueError
        If ``path`` does not have an image extension.
    RuntimeError
        If there is a network error, API error or the response is malformed.
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError(
            "Unsupported format: only .jpeg, .jpg or .png images are allowed",
        )

    api_key = get_gemini_api_key()

    try:
        from google import genai  # type: ignore

        client = genai.Client(api_key=api_key)

        with open(path, "rb") as fh:
            image_bytes = fh.read()

        mime_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"

        prompt = (
            "Analiza el comprobante y responde únicamente con un JSON con el "
            "formato {\"items\": [{\"descripcion\": \"\", "
            "\"cantidad\": 1, \"precio_unitario\": 1.0}]}."
        )

        response = client.responses.generate(
            model="gemini-1.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_bytes,
                            }
                        },
                    ],
                }
            ],
        )

        raw_json = response.output_text  # type: ignore[attr-defined]
        data = json.loads(raw_json)
    except Exception as exc:  # pragma: no cover - network/API errors
        raise RuntimeError(f"Error al comunicarse con Gemini: {exc}") from exc

    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise RuntimeError("Respuesta inválida del servicio Gemini")

    normalised: List[Dict] = []
    for item in items:
        desc = item.get("descripcion") or item.get("producto") or ""
        try:
            cantidad = float(item.get("cantidad", 0))
        except Exception:  # pragma: no cover - defensive
            cantidad = 0.0
        try:
            precio = float(item.get("precio_unitario", item.get("precio", 0)))
        except Exception:  # pragma: no cover - defensive
            precio = 0.0
        normalised.append({"producto": desc, "cantidad": cantidad, "precio": precio})

    return normalised
