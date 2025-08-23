import unittest
from unittest.mock import patch

from controllers import compras_controller
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor


class TestCompraDesdeImagenGUI(unittest.TestCase):
    @patch('controllers.compras_controller.receipt_parser.parse_receipt_image')
    def test_aceptar_items_actualiza_lista_y_total(self, mock_parse):
        mock_parse.return_value = (
            [
                {"producto_id": 1, "nombre_producto": "Cafe", "cantidad": 1, "costo_unitario": 10},
                {"producto_id": 2, "nombre_producto": "Azucar", "cantidad": 3, "costo_unitario": 5},
            ],
            [],
        )

        proveedor = Proveedor('Proveedor')
        items, pendientes = compras_controller.registrar_compra_desde_imagen(proveedor, 'img.jpg')
        self.assertEqual(pendientes, [])
        compra_actual_items = []

        # Aceptar primer ítem
        compra_actual_items.append(
            CompraDetalle(
                producto_id=items[0]["producto_id"],
                nombre_producto=items[0]["nombre_producto"],
                cantidad=items[0]["cantidad"],
                costo_unitario=items[0]["costo_unitario"],
                descripcion_adicional=items[0].get("descripcion_adicional", ""),
            )
        )
        total = sum(i.total for i in compra_actual_items)
        self.assertEqual(len(compra_actual_items), 1)
        self.assertEqual(total, 10)

        # Aceptar segundo ítem
        compra_actual_items.append(
            CompraDetalle(
                producto_id=items[1]["producto_id"],
                nombre_producto=items[1]["nombre_producto"],
                cantidad=items[1]["cantidad"],
                costo_unitario=items[1]["costo_unitario"],
                descripcion_adicional=items[1].get("descripcion_adicional", ""),
            )
        )
        total = sum(i.total for i in compra_actual_items)
        self.assertEqual(len(compra_actual_items), 2)
        self.assertEqual(total, 10 + 15)


if __name__ == '__main__':
    unittest.main()
