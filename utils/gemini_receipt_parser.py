"""Receipt parser powered by the Gemini API.

This module is a placeholder for a future implementation that will use
Google's Gemini models to extract structured data from receipt images."""

from __future__ import annotations

from typing import Dict, List


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
    NotImplementedError
        The Gemini backend is not available in this test environment.
    """

    raise NotImplementedError(
        "El backend de Gemini para analizar comprobantes aún no está implementado"
    )
