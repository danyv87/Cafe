import json
import pytest

from utils import receipt_parser
from utils.receipt_parser import parse_receipt_image


def test_parse_receipt_image_json_file_not_found():
    with pytest.raises(ValueError, match="Archivo JSON de recibo no encontrado"):
        parse_receipt_image("no_existe.json")


def test_parse_receipt_image_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid}")
    with pytest.raises(ValueError, match="JSON de recibo inválido"):
        parse_receipt_image(str(bad_file))


def test_parse_receipt_image_json_with_metadata(tmp_path, monkeypatch):
    data = {
        "proveedor": "Proveedor SA",
        "numero_comprobante": "001-001-000123",
        "fecha": "2024-01-02",
        "total": 1000,
        "items": [{"producto": "Azucar", "cantidad": 1, "precio": 1000}],
    }
    file = tmp_path / "factura.json"
    file.write_text(json.dumps(data))

    # Avoid heavy dependencies during normalisation
    monkeypatch.setattr(receipt_parser, "_normalizar_items", lambda raw, omitidos=None: ([], []))

    items, faltantes, meta = parse_receipt_image(str(file))

    assert items == [] and faltantes == []
    assert meta["proveedor"] == "Proveedor SA"
    assert meta["total"] == 1000
    assert meta["fecha"] == "2024-01-02"
