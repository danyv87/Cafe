"""Utilities for parsing receipt images.

This module exposes ``parse_receipt_image`` which is expected to take a path to an
image and return a list of dictionaries representing purchase items. The
implementation may rely on external services or OCR libraries. In tests this
function is commonly patched to provide deterministic results."""

from typing import List, Dict


def parse_receipt_image(path_imagen: str) -> List[Dict]:
    """Parse a receipt image and return a list of item dictionaries.

    This is a placeholder implementation that should be replaced with an
    actual parser. It exists so that other modules can import it and tests can
    patch it accordingly.
    """
    raise NotImplementedError("parse_receipt_image debe implementarse externamente")
