import unittest
from unittest.mock import patch

from tkinter import messagebox

from controllers import compras_controller
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor


class TestCompraDesdeImagenGUI(unittest.TestCase):
    @patch('tkinter.messagebox.showinfo')
    @patch('controllers.compras_controller.receipt_parser.parse_receipt_image')
    def test_aceptar_items_actualiza_lista_y_total(self, mock_parse, mock_showinfo):
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

        def aceptar_items(indices):
            for idx in indices:
                compra_actual_items.append(CompraDetalle(**items[idx]))
            messagebox.showinfo("Éxito", f"Se agregaron {len(indices)} ítems importados.")

        # Aceptar primer ítem
        aceptar_items([0])
        total = sum(i.total for i in compra_actual_items)
        self.assertEqual(len(compra_actual_items), 1)
        self.assertEqual(total, 10)
        self.assertEqual(
            mock_showinfo.call_args_list[0][0][1],
            "Se agregaron 1 ítems importados.",
        )

        # Aceptar segundo ítem
        aceptar_items([1])
        total = sum(i.total for i in compra_actual_items)
        self.assertEqual(len(compra_actual_items), 2)
        self.assertEqual(total, 10 + 15)
        self.assertEqual(
            mock_showinfo.call_args_list[1][0][1],
            "Se agregaron 1 ítems importados.",
        )


if __name__ == '__main__':
    unittest.main()
