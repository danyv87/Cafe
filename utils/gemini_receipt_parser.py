"""Receipt parser powered by Gemini.

This module exposes :func:`parse_receipt_image` which sends a receipt image to
Google's Gemini generative AI models to obtain a textual transcription.  Lines
containing product information are then matched with regular expressions to
extract ``producto``, ``cantidad`` and ``precio`` fields.

The Gemini API key is retrieved via :func:`utils.gemini_api.get_gemini_api_key`.
Ensure the key is available and the ``google-generativeai`` package is
installed.
"""

from __future__ import annotations

import os
import re
from typing import List, Dict

import google.generativeai as genai

from .gemini_api import get_gemini_api_key

_SUMMARY_KEYWORDS = {"total", "subtotal", "iva"}


def _normalise_number(value: str) -> float:
    value = value.replace("$", "").replace(",", ".")
    return float(value)


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image and extract purchased items.

    The function loads the image from ``path`` and sends it to Gemini to obtain
    the text. Each line is analysed with a regular expression expecting the
    structure ``producto cantidad precio`` where the numeric values may contain
    decimal points. Matching lines are converted to dictionaries with the keys
    ``producto``, ``cantidad`` and ``precio``. If a line does not match this
    pattern, a heuristic fallback is applied that extracts the last two numeric
    values as quantity and price respectively. Lines containing keywords such as
    ``Total`` or ``IVA`` are ignored to reduce false positives from summary
    sections.

    Parameters
    ----------
    path:
        Path to an image (``.jpeg``, ``.jpg`` or ``.png``) containing the
        receipt.

    Returns
    -------
    list of dict
        A list of dictionaries describing the items.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the path does not end with ``.jpeg``, ``.jpg`` or ``.png``.
    RuntimeError
        If the Gemini API request fails or returns no text.
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError(
            "Unsupported format: only .jpeg, .jpg or .png images are allowed"
        )

    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    mime_type = "image/jpeg" if path.lower().endswith((".jpeg", ".jpg")) else "image/png"
    with open(path, "rb") as fh:
        image_bytes = fh.read()

    response = model.generate_content(
        [
            {"mime_type": mime_type, "data": image_bytes},
            "Transcribe el texto del recibo en español. Devuelve solo el texto.",
        ]
    )
    text = getattr(response, "text", "")
    if not text:
        raise RuntimeError("No se pudo obtener texto del recibo usando Gemini")

    pattern = re.compile(
        r"^(?P<producto>.+?)\s+(?P<cantidad>\d+(?:[.,]\d+)?)\s+(?P<precio>\d+(?:[.,]\d+)?)(?:\s+\w+)?$"
    )
    items: List[Dict] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or any(k in line.lower() for k in _SUMMARY_KEYWORDS):
            continue

        match = pattern.match(line)
        if match:
            producto = match.group("producto").strip()
            cantidad_txt = match.group("cantidad")
            precio_txt = match.group("precio")
        else:
            cleaned = line.replace("$", "")
            numbers = re.findall(r"\d+(?:[.,]\d+)?", cleaned)
            if len(numbers) < 2:
                continue
            precio_txt = numbers[-1]
            cantidad_txt = numbers[-2]
            idx_precio = cleaned.rfind(precio_txt)
            before_precio = cleaned[:idx_precio].rstrip()
            idx_cantidad = before_precio.rfind(cantidad_txt)
            producto = before_precio[:idx_cantidad].strip()
            if not producto:
                continue

        try:
            cantidad = _normalise_number(cantidad_txt)
            precio = _normalise_number(precio_txt)
        except ValueError:
            continue

        items.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "precio": precio,
            }
        )

    return items
