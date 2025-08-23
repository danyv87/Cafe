import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from controllers import compras_controller
from controllers.invoice_importer import InvoiceImporter
from models.proveedor import Proveedor


@patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
def test_registrar_compra_desde_imagen_guarda_factura(mock_parse, tmp_path):
    mock_parse.return_value = (
        [
            {
                "producto_id": uuid4().hex,
                "nombre_producto": "Cafe",
                "cantidad": 2,
                "costo_unitario": 5,
            }
        ],
        [],
        {},
    )

    proveedor = Proveedor("Proveedor")
    compras_controller.registrar_compra_desde_imagen(
        proveedor, "img.jpg", output_dir=tmp_path
    )

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["proveedor"] == "Proveedor"
    assert data["proveedor_id"] == proveedor.id
    assert data["items"][0]["nombre_producto"] == "Cafe"


@patch("utils.invoice_utils.save_invoice", side_effect=RuntimeError("db down"))
def test_invoice_importer_persist_failure(mock_save, tmp_path):
    importer = InvoiceImporter()
    with pytest.raises(RuntimeError, match="No se pudo guardar la factura"):
        importer.persist({}, tmp_path)
    mock_save.assert_called_once()


@patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
def test_registrar_compra_desde_imagen_persist_error(mock_parse, tmp_path):
    mock_parse.return_value = (
        [
            {
                "producto_id": uuid4().hex,
                "nombre_producto": "Cafe",
                "cantidad": 1,
                "costo_unitario": 5,
            }
        ],
        [],
        {},
    )
    proveedor = Proveedor("Proveedor")
    with patch(
        "utils.invoice_utils.save_invoice", side_effect=RuntimeError("db down")
    ):
        with pytest.raises(ValueError, match="No se pudo guardar la factura"):
            compras_controller.registrar_compra_desde_imagen(
                proveedor, "img.jpg", output_dir=tmp_path
            )
