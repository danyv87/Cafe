from pathlib import Path

import pytest
pytest.importorskip("PIL")
from PIL import Image, ImageDraw

from utils import gpt_receipt_parser
import shutil


def _create_receipt_image(path: Path) -> None:
    """Create a simple receipt image for testing purposes.

    The image contains two lines, each with ``producto cantidad precio``
    separated by spaces so the regex in :mod:`utils.gpt_receipt_parser` can pick
    them up reliably.
    """

    img = Image.new("RGB", (200, 80), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Cafe 1 2", fill="black")
    draw.text((10, 40), "Leche 2 3", fill="black")
    img.save(path)


def test_parse_receipt_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        gpt_receipt_parser.parse_receipt_image("missing.png")


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")
def test_parse_receipt_image_extracts_items(tmp_path):
    img_path = tmp_path / "receipt.png"
    _create_receipt_image(img_path)

    items = gpt_receipt_parser.parse_receipt_image(str(img_path))

    assert {
        "producto": "Cafe",
        "cantidad": 1.0,
        "precio": 2.0,
    } in items
    assert {
        "producto": "Leche",
        "cantidad": 2.0,
        "precio": 3.0,
    } in items

