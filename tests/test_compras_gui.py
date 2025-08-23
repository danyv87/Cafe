import unittest
from unittest.mock import patch

from tkinter import messagebox

from controllers import compras_controller
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor
from models.compra import Compra


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


class TestGestionComprasGUI(unittest.TestCase):
    def test_eliminar_compra_actualiza_lista(self):
        import gui.gestion_compras as gestion_compras

        compras = [Compra(proveedor_id="Prov1"), Compra(proveedor_id="Prov2")]
        compras[0].total = 100
        compras[1].total = 200

        def fake_listar():
            return compras

        def fake_eliminar(cid):
            compras[:] = [c for c in compras if c.id != cid]

        listbox_holder = {}

        class DummyListbox:
            def __init__(self, *a, **k):
                self.items = []
                self.selection = ()
                listbox_holder['instance'] = self

            def pack(self, *a, **k):
                pass

            def delete(self, start, end=None):
                self.items = []

            def insert(self, index, item):
                self.items.append(item)

            def curselection(self):
                return self.selection

            def selection_set(self, idx):
                self.selection = (idx,)

            def get(self, idx):
                return self.items[idx]

            def size(self):
                return len(self.items)

        class DummyToplevel:
            def __init__(self):
                pass

            def title(self, t):
                pass

            def geometry(self, g):
                pass

        class DummyLabel:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

        with patch('gui.gestion_compras.tk.Toplevel', DummyToplevel), \
             patch('gui.gestion_compras.tk.Label', DummyLabel), \
             patch('gui.gestion_compras.tk.Listbox', DummyListbox), \
             patch('gui.gestion_compras.tk.Button') as MockButton, \
             patch('gui.gestion_compras.listar_compras', side_effect=fake_listar), \
             patch('gui.gestion_compras.eliminar_compra', side_effect=fake_eliminar), \
             patch('gui.gestion_compras.messagebox') as mock_msg:
            mock_msg.askyesno.return_value = True
            gestion_compras.mostrar_ventana_gestion_compras()
            lista = listbox_holder['instance']
            self.assertEqual(lista.size(), 2)
            self.assertIn("Proveedor: Prov1", lista.get(0))
            self.assertIn("Proveedor: Prov2", lista.get(1))

            lista.selection_set(0)
            eliminar_func = MockButton.call_args.kwargs['command']
            eliminar_func()

            self.assertEqual(lista.size(), 1)
            self.assertIn("Proveedor: Prov2", lista.get(0))
            mock_msg.askyesno.assert_called_once()

if __name__ == '__main__':
    unittest.main()

