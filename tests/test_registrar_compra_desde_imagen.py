import pytest
from unittest.mock import patch

from controllers import compras_controller
from models.compra import Compra
from models.compra_detalle import CompraDetalle


@patch("controllers.compras_controller.parse_receipt_image")
def test_registrar_compra_desde_imagen_ok(mock_parse):
    mock_parse.return_value = [
        {
            "producto_id": 1,
            "nombre_producto": "Cafe",
            "cantidad": 2,
            "costo_unitario": 5,
        }
    ]

    compra = compras_controller.registrar_compra_desde_imagen(
        "Proveedor", "img.jpg", como_compra=True
    )
    assert isinstance(compra, Compra)
    assert len(compra.items_compra) == 1
    detalle = compra.items_compra[0]
    assert isinstance(detalle, CompraDetalle)
    assert detalle.nombre_producto == "Cafe"


@patch(
    "controllers.compras_controller.parse_receipt_image",
    side_effect=ConnectionError("network"),
)
def test_registrar_compra_desde_imagen_network_error(mock_parse):
    with pytest.raises(ValueError):
        compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")


@patch(
    "controllers.compras_controller.parse_receipt_image",
    side_effect=FileNotFoundError("missing"),
)
def test_registrar_compra_desde_imagen_archivo_no_encontrado(mock_parse):
    with pytest.raises(ValueError, match="El comprobante no existe o no es accesible."):
        compras_controller.registrar_compra_desde_imagen("Proveedor", "no_file.json")


@patch("controllers.compras_controller.parse_receipt_image")
def test_registrar_compra_desde_imagen_datos_malos(mock_parse):
    mock_parse.return_value = {"producto": "mal"}  # no es una lista
    with pytest.raises(ValueError):
        compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")


@patch("controllers.compras_controller.parse_receipt_image")
@pytest.mark.parametrize("producto_id", [None, "", 0, "abc"])
def test_registrar_compra_desde_imagen_producto_id_invalido(mock_parse, producto_id):
    mock_parse.return_value = [
        {
            "producto_id": producto_id,
            "nombre_producto": "Cafe",
            "cantidad": 1,
            "costo_unitario": 5,
        }
    ]

    with pytest.raises(ValueError):
        compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")
