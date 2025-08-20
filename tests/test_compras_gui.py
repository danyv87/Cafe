import unittest
from unittest.mock import patch

from controllers import compras_controller
from gui import compras_view


class TestCompraDesdeImagenGUI(unittest.TestCase):
    @patch('controllers.compras_controller.receipt_parser.parse_receipt_image')
    def test_crear_detalles_desde_items_seleccion(self, mock_parse):
        mock_parse.return_value = [
            {"producto_id": 1, "nombre_producto": "Cafe", "cantidad": 1, "costo_unitario": 10},
            {"producto_id": None, "nombre_producto": "Azucar", "cantidad": 3, "costo_unitario": 5},
        ]

        validos, pendientes = compras_controller.registrar_compra_desde_imagen('Proveedor', 'img.jpg')
        items = validos + pendientes

        # Seleccionar solo el primer ítem válido
        detalles = compras_view.crear_detalles_desde_items(items, [True, False])
        self.assertEqual(len(detalles), 1)
        self.assertEqual(detalles[0].nombre_producto, 'Cafe')

        # Seleccionar ambos ítems, pero el segundo no tiene materia prima
        detalles = compras_view.crear_detalles_desde_items(items, [True, True])
        self.assertEqual(len(detalles), 1)
        total = sum(d.total for d in detalles)
        self.assertEqual(total, 10)


if __name__ == '__main__':
    unittest.main()
