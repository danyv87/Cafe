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


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image and extract purchased items.

    The function loads the image from ``path`` and uses Tesseract to obtain the
    text.  Each line is analysed with a regular expression expecting the
    structure ``producto cantidad precio`` where the numeric values may contain
    decimal points.  Matching lines are converted to dictionaries with the keys
    ``producto``, ``cantidad`` and ``precio``.

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

    # Expect lines formatted as: ``<producto> <cantidad> <precio>``
    pattern = re.compile(
        r"^(?P<producto>.+?)\s+(?P<cantidad>\d+(?:\.\d+)?)\s+(?P<precio>\d+(?:\.\d+)?)$"
    )
    items: List[Dict] = []
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        try:
            cantidad = float(match.group("cantidad"))
            precio = float(match.group("precio"))
        except ValueError:
            # Skip lines with malformed numbers
            continue
        items.append(
            {
                "producto": match.group("producto").strip(),
                "cantidad": cantidad,
                "precio": precio,
            }
        )

    return items

