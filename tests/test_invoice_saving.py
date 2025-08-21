import json
from unittest.mock import patch

from controllers import compras_controller


@patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
def test_registrar_compra_desde_imagen_guarda_factura(mock_parse, tmp_path):
    mock_parse.return_value = (
        [
            {
                "producto_id": 1,
                "nombre_producto": "Cafe",
                "cantidad": 2,
                "costo_unitario": 5,
            }
        ],
        [],
    )

    compras_controller.registrar_compra_desde_imagen(
        "Proveedor", "img.jpg", output_dir=tmp_path
    )

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["proveedor"] == "Proveedor"
    assert data["items"][0]["nombre_producto"] == "Cafe"
