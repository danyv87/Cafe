import json
from unittest.mock import patch

from controllers import compras_controller
from models.proveedor import Proveedor


@patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
def test_registrar_compra_desde_imagen_guarda_factura(mock_parse, tmp_path):
    mock_parse.return_value = iter(
        [
            (
                {
                    "producto_id": 1,
                    "nombre_producto": "Cafe",
                    "cantidad": 2,
                    "costo_unitario": 5,
                },
                None,
            )
        ]
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
