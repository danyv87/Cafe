from unittest.mock import patch

from controllers import compras_controller
from models.compra import Compra
from models.proveedor import Proveedor
from models.compra_detalle import CompraDetalle
from utils.invoice_utils import save_invoice


def _invoice_data():
    return {
        "proveedor_id": "prov-1",
        "proveedor": "Proveedor Uno",
        "fecha": "2024-05-01 12:00:00",
        "items": [
            {
                "producto_id": "mp-1",
                "nombre_producto": "Azucar",
                "cantidad": 3,
                "costo_unitario": 10,
                "descripcion_adicional": "blanca",
            }
        ],
    }


@patch("controllers.compras_controller.registrar_compra")
def test_importar_factura_desde_directorio(mock_registrar, tmp_path):
    inv = _invoice_data()
    invoice_id = save_invoice(inv, tmp_path)

    expected_compra = Compra(proveedor_id=inv["proveedor_id"], items_compra=[])
    mock_registrar.return_value = expected_compra

    resultado = compras_controller.importar_factura(tmp_path, invoice_id)

    assert resultado is expected_compra

    mock_registrar.assert_called_once()
    proveedor_arg, detalles_arg = mock_registrar.call_args[0]
    fecha_kw = mock_registrar.call_args.kwargs.get("fecha")

    assert isinstance(proveedor_arg, Proveedor)
    assert proveedor_arg.id == inv["proveedor_id"]
    assert proveedor_arg.nombre == inv["proveedor"]

    assert isinstance(detalles_arg, list) and len(detalles_arg) == 1
    detalle = detalles_arg[0]
    assert isinstance(detalle, CompraDetalle)
    item = inv["items"][0]
    assert detalle.producto_id == item["producto_id"]
    assert detalle.nombre_producto == item["nombre_producto"]
    assert detalle.cantidad == item["cantidad"]
    assert detalle.costo_unitario == item["costo_unitario"]
    assert detalle.descripcion_adicional == item["descripcion_adicional"]

    assert fecha_kw == inv["fecha"]

