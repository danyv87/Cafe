"""OCR based receipt parser using Tesseract.

This module exposes :func:`parse_receipt_image` which relies on the
`pytesseract` wrapper around the Tesseract OCR engine to extract text from an
image of a purchase receipt.  Lines containing product information are then
matched with regular expressions to obtain ``producto``, ``cantidad`` and
``precio`` fields.

The Tesseract binary must be available in the system.  If the language data is
stored in a non standard location, set the ``TESSDATA_PREFIX`` environment
variable to point to the directory containing the ``tessdata`` folder.
"""

from __future__ import annotations

import os
import re
from typing import List, Dict

from PIL import Image
import pytesseract

_SUMMARY_KEYWORDS = {"total", "subtotal", "iva"}


def _normalise_number(value: str) -> float:
    value = value.replace("$", "").replace(",", ".")
    return float(value)


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image and extract purchased items.

    The function loads the image from ``path`` and uses Tesseract to obtain the
    text.  Each line is analysed with a regular expression expecting the
    structure ``producto cantidad precio`` where the numeric values may contain
    decimal points.  Matching lines are converted to dictionaries with the keys
    ``producto``, ``cantidad`` and ``precio``.  If a line does not match this
    pattern, a heuristic fallback is applied that extracts the last two numeric
    values as quantity and price respectively.  Lines containing keywords such
    as ``Total`` or ``IVA`` are ignored to reduce false positives from summary
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
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError(
            "Unsupported format: only .jpeg, .jpg or .png images are allowed"
        )

    image = Image.open(path)
    text = pytesseract.image_to_string(image)

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

