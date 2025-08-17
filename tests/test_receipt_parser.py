import pytest

from utils.receipt_parser import parse_receipt_image


def test_parse_receipt_image_json_file_not_found():
    with pytest.raises(ValueError, match="Archivo JSON de recibo no encontrado"):
        parse_receipt_image("no_existe.json")


def test_parse_receipt_image_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid}")
    with pytest.raises(ValueError, match="JSON de recibo inválido"):
        parse_receipt_image(str(bad_file))
