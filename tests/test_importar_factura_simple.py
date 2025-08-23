from unittest.mock import patch

from controllers import compras_controller
from models.proveedor import Proveedor
from models.compra import Compra


@patch("controllers.compras_controller.registrar_compra_desde_imagen")
def test_importar_factura_simple_delega(mock_registrar, tmp_path):
    mock_registrar.return_value = ("compra", [], {})
    proveedor = Proveedor("Prov")
    result = compras_controller.importar_factura_simple(
        proveedor, "img.jpg", destino=tmp_path
    )
    assert result == ("compra", [])
    mock_registrar.assert_called_once_with(
        proveedor,
        "img.jpg",
        como_compra=True,
        output_dir=tmp_path,
        db_conn=None,
        omitidos=None,
        selector=None,
    )


@patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
def test_importar_factura_simple_flujo_basico(mock_parse):
    mock_parse.return_value = (
        [
            {
                "producto_id": "1",
                "nombre_producto": "Cafe",
                "cantidad": 1,
                "costo_unitario": 10,
            }
        ],
        [],
        {},
    )
    proveedor = Proveedor("Proveedor")
    compra, pendientes = compras_controller.importar_factura_simple(
        proveedor, "img.jpg"
    )
    assert pendientes == []
    assert isinstance(compra, Compra)
    assert compra.items_compra[0].nombre_producto == "Cafe"
