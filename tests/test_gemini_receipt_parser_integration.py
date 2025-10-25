import pytest
from types import SimpleNamespace

from utils import receipt_parser


def test_parse_receipt_image_missing_quantity_or_price(monkeypatch, tmp_path):
    # Create dummy image file expected by the parser
    dummy_img = tmp_path / "receipt.png"
    dummy_img.touch()

    # Fake Gemini backend returning items with missing fields
    def fake_gemini_parse(path: str):
        # Simulate response JSON from Client with incomplete data
        return [
            {"producto": "Cafe", "precio": 2.5},  # missing "cantidad"
            {"producto": "Azucar", "cantidad": 1.0},  # missing "precio"
        ]

    monkeypatch.setattr(
        "utils.gemini_receipt_parser.parse_receipt_image", fake_gemini_parse
    )

    # Avoid dependence on controllers by returning a dummy object
    def fake_buscar(nombre: str):
        return SimpleNamespace(id=1, nombre=nombre)

    monkeypatch.setattr("utils.receipt_parser._buscar_materia_prima", fake_buscar)

    with pytest.raises(ValueError):
        receipt_parser.parse_receipt_image(str(dummy_img))
