"""Receipt parser powered by the Gemini API.

This module communicates with Google's Gemini models to extract structured
data from receipt images.  It relies on the external ``google-genai`` package
and the :func:`utils.gemini_api.get_gemini_api_key` helper to obtain the
authentication token from a safe location.
"""

from __future__ import annotations

import os
from typing import Dict, List

from .gemini_api import get_gemini_api_key


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
    NotImplementedError
        The Gemini backend is not available in this test environment.
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

    raise NotImplementedError(
        "El backend de Gemini para analizar comprobantes aún no está implementado"
    )
