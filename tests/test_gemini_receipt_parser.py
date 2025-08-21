from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from utils import gpt_receipt_parser


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


def _create_complex_receipt_image(path: Path) -> None:
    """Create a receipt image containing multiple items, including an unknown one.

    Besides the original two products, this helper adds extra lines so tests can
    simulate a receipt with more entries.  The last line contains a product name
    that our application does not recognise, useful to verify that later stages
    in the flow can omit it if the user decides so.
    """

    img = Image.new("RGB", (200, 140), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Cafe 1 2", fill="black")
    draw.text((10, 40), "Leche 2 3", fill="black")
    draw.text((10, 70), "Azucar 3 5", fill="black")
    draw.text((10, 100), "Desconocido 1 7", fill="black")
    img.save(path)


def test_parse_receipt_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        gpt_receipt_parser.parse_receipt_image("missing.png")


def test_parse_receipt_image_extracts_items(tmp_path, monkeypatch):
    img_path = tmp_path / "receipt.png"
    _create_receipt_image(img_path)

    monkeypatch.setattr(
        "utils.gpt_receipt_parser.pytesseract.image_to_string",
        lambda img, lang="spa": "Cafe 1 2\nLeche 2 3",
    )

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


def test_parse_receipt_image_multiple_items(tmp_path, monkeypatch):
    img_path = tmp_path / "receipt_multi.png"
    _create_complex_receipt_image(img_path)

    monkeypatch.setattr(
        "utils.gpt_receipt_parser.pytesseract.image_to_string",
        lambda img, lang="spa": "Cafe 1 2\nLeche 2 3\nAzucar 3 5\nDesconocido 1 7",
    )

    items = gpt_receipt_parser.parse_receipt_image(str(img_path))

    assert len(items) == 4
    assert {
        "producto": "Azucar",
        "cantidad": 3.0,
        "precio": 5.0,
    } in items
    assert {
        "producto": "Desconocido",
        "cantidad": 1.0,
        "precio": 7.0,
    } in items


def test_parse_receipt_image_varied_formats(tmp_path, monkeypatch):
    img_path = tmp_path / "receipt_varied.png"
    _create_receipt_image(img_path)

    monkeypatch.setattr(
        "utils.gpt_receipt_parser.pytesseract.image_to_string",
        lambda img, lang="spa": (
            "BANANA 70999 kg 0.970 82.50\n"
            "Azucar 1 3,50\n"
            "Manteca 2 $7,25\n"
            "Subtotal 89,25\nTotal 89,25"
        ),
    )

    items = gpt_receipt_parser.parse_receipt_image(str(img_path))

    assert len(items) == 3
    assert {
        "producto": "BANANA 70999 kg",
        "cantidad": 0.97,
        "precio": 82.5,
    } in items
    assert {
        "producto": "Azucar",
        "cantidad": 1.0,
        "precio": 3.5,
    } in items
    assert {
        "producto": "Manteca",
        "cantidad": 2.0,
        "precio": 7.25,
    } in items

