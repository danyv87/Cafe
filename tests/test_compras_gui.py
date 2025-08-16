import unittest
from unittest.mock import patch

from controllers import compras_controller
from models.compra_detalle import CompraDetalle


class TestCompraDesdeImagenGUI(unittest.TestCase):
    @patch('controllers.compras_controller.parse_receipt_image')
    def test_aceptar_items_actualiza_lista_y_total(self, mock_parse):
        mock_parse.return_value = [
            {"producto_id": 1, "nombre_producto": "Cafe", "cantidad": 1, "costo_unitario": 10},
            {"producto_id": 2, "nombre_producto": "Azucar", "cantidad": 3, "costo_unitario": 5},
        ]

        items = compras_controller.registrar_compra_desde_imagen('Proveedor', 'img.jpg')
        compra_actual_items = []

        # Aceptar primer ítem
        compra_actual_items.append(CompraDetalle(**items[0]))
        total = sum(i.total for i in compra_actual_items)
        self.assertEqual(len(compra_actual_items), 1)
        self.assertEqual(total, 10)

        # Aceptar segundo ítem
        compra_actual_items.append(CompraDetalle(**items[1]))
        total = sum(i.total for i in compra_actual_items)
        self.assertEqual(len(compra_actual_items), 2)
        self.assertEqual(total, 10 + 15)


if __name__ == '__main__':
    unittest.main()
