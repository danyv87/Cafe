import unittest
from unittest.mock import patch
from uuid import uuid4

from tkinter import messagebox

from controllers import compras_controller
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor
from models.compra import Compra


class TestCompraDesdeImagenGUI(unittest.TestCase):
    @patch('tkinter.messagebox.showinfo')
    @patch('controllers.compras_controller.receipt_parser.parse_receipt_image')
    def test_aceptar_items_actualiza_lista_y_total(self, mock_parse, mock_showinfo):
        id_cafe = uuid4().hex
        id_azucar = uuid4().hex
        mock_parse.return_value = (
            [
                {"producto_id": id_cafe, "nombre_producto": "Cafe", "cantidad": 1, "costo_unitario": 10},
                {"producto_id": id_azucar, "nombre_producto": "Azucar", "cantidad": 3, "costo_unitario": 5},
            ],
            [],
            {},
        )

        proveedor = Proveedor('Proveedor')
        items, pendientes, meta = compras_controller.registrar_compra_desde_imagen(proveedor, 'img.jpg')
        self.assertEqual(pendientes, [])
        self.assertEqual(meta, {})
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

    def test_items_deseleccionados_no_agregados(self):
        import gui.compras_view as compras_view

        items_data = [
            {"producto_id": "id1", "nombre_producto": "Item1", "cantidad": 1, "costo_unitario": 10},
            {"producto_id": "id2", "nombre_producto": "Item2", "cantidad": 2, "costo_unitario": 20},
        ]

        created = []

        class DummyCompraDetalle:
            def __init__(self, producto_id, nombre_producto, cantidad, costo_unitario, descripcion_adicional=""):
                self.producto_id = producto_id
                self.nombre_producto = nombre_producto
                self.cantidad = cantidad
                self.costo_unitario = costo_unitario
                self.descripcion_adicional = descripcion_adicional
                self.total = round(cantidad * costo_unitario, 2)
                created.append(self)

        class DummyToplevel:
            def __init__(self, *a, **k):
                pass

            def title(self, *a):
                pass

            def geometry(self, *a):
                pass

            def attributes(self, *a, **k):
                pass

            def after(self, delay, func):
                func()

            def wait_window(self, *a):
                pass

            def pack(self, *a, **k):
                pass

            def destroy(self):
                pass

            def transient(self, *a):
                pass

            def grab_set(self):
                pass

        class DummyFrame:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

        class DummyScrollbar:
            def __init__(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

            def set(self, *a, **k):
                pass

        class DummyListbox:
            instances = []

            def __init__(self, *a, **k):
                self.items = []
                self.selection = ()
                DummyListbox.instances.append(self)

            def pack(self, *a, **k):
                pass

            def delete(self, start, end=None):
                self.items = []

            def insert(self, index, item):
                self.items.append(item)

            def curselection(self):
                return self.selection

            def selection_set(self, start, end=None):
                if end is None:
                    self.selection = (start,)
                else:
                    self.selection = tuple(range(start, end + 1))

            def selection_clear(self, start, end=None):
                self.selection = ()

            def size(self):
                return len(self.items)

            def yview(self, *a, **k):
                pass

            def bind(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

        class DummyButton:
            instances = []

            def __init__(self, *a, **k):
                self.command = k.get('command')
                self.text = k.get('text')
                DummyButton.instances.append(self)

            def pack(self, *a, **k):
                pass

        class DummyLabel:
            instances = []

            def __init__(self, *a, **k):
                self.text = k.get('text')
                DummyLabel.instances.append(self)

            def pack(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

        class DummyEntry:
            instances = []

            def __init__(self, *a, **k):
                self.value = ""
                DummyEntry.instances.append(self)

            def pack(self, *a, **k):
                pass

            def get(self):
                return self.value

            def insert(self, index, value):
                self.value = value

            def delete(self, start, end=None):
                self.value = ""

            def bind(self, *a, **k):
                pass

        class DummyProgressbar:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        class DummyThread:
            def __init__(self, target, daemon=False):
                self.target = target

            def start(self):
                self.target()

            def is_alive(self):
                return False

        class DummyCheckbutton:
            instances = []

            def __init__(self, *a, **k):
                self.variable = k.get('variable')
                self.text = k.get('text')
                DummyCheckbutton.instances.append(self)

            def pack(self, *a, **k):
                pass

        class DummyBooleanVar:
            def __init__(self, value=False):
                self.value = value

            def get(self):
                return self.value

            def set(self, val):
                self.value = val

        mp_fake = type('MP', (), {'unidad_medida': 'u'})()

        with patch('gui.compras_view.CompraDetalle', DummyCompraDetalle), \
             patch('gui.compras_view.registrar_compra_desde_imagen', return_value=(items_data, [], {})), \
             patch('gui.compras_view.filedialog.askopenfilename', return_value='test.png'), \
             patch('gui.compras_view.messagebox'), \
             patch('gui.compras_view.listar_materias_primas', return_value=[]), \
             patch('gui.compras_view.obtener_materia_prima_por_id', return_value=mp_fake), \
             patch('gui.compras_view.DateEntry', DummyEntry), \
             patch('gui.compras_view.ttk.Label', DummyLabel), \
             patch('gui.compras_view.ttk.Progressbar', DummyProgressbar), \
             patch('gui.compras_view.ttk.Checkbutton', DummyCheckbutton), \
             patch('gui.compras_view.threading.Thread', DummyThread), \
             patch.multiple('gui.compras_view.tk', Toplevel=DummyToplevel, Frame=DummyFrame, Scrollbar=DummyScrollbar, Listbox=DummyListbox, Button=DummyButton, Label=DummyLabel, Entry=DummyEntry, BooleanVar=DummyBooleanVar):
            compras_view.mostrar_ventana_compras()
            DummyEntry.instances[0].insert(0, 'Proveedor')
            import_btn = next(b for b in DummyButton.instances if b.text == 'Importar desde imagen')
            import_btn.command()
            DummyCheckbutton.instances[0].variable.set(False)
            agregar_btn = next(b for b in DummyButton.instances if b.text == 'Agregar a la compra')
            agregar_btn.command()
            self.assertEqual(len(created), 1)
            self.assertEqual(created[0].nombre_producto, 'Item2')

    def test_preview_muestra_antes_de_solicitar_faltantes(self):
        import gui.compras_view as compras_view

        items_data = [
            {"producto_id": "id1", "nombre_producto": "Item1", "cantidad": 1, "costo_unitario": 10},
        ]
        faltantes_data = [{"nombre_producto": "Falta1"}]

        class DummyCompraDetalle:
            def __init__(self, *a, **k):
                pass

        class DummyToplevel:
            def __init__(self, *a, **k):
                pass

            def title(self, *a):
                pass

            def geometry(self, *a):
                pass

            def attributes(self, *a, **k):
                pass

            def after(self, delay, func):
                func()

            def wait_window(self, *a):
                pass

            def pack(self, *a, **k):
                pass

            def destroy(self):
                pass

            def transient(self, *a):
                pass

            def grab_set(self):
                pass

        class DummyFrame:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

        class DummyScrollbar:
            def __init__(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

            def set(self, *a, **k):
                pass

        class DummyListbox:
            def __init__(self, *a, **k):
                self.items = []

            def pack(self, *a, **k):
                pass

            def delete(self, start, end=None):
                self.items = []

            def insert(self, index, item):
                self.items.append(item)

            def yview(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

            def bind(self, *a, **k):
                pass

            def size(self):
                return len(self.items)

            def curselection(self):
                return ()

            def selection_set(self, start, end=None):
                pass

            def selection_clear(self, start, end=None):
                pass

        class DummyButton:
            instances = []

            def __init__(self, *a, **k):
                self.command = k.get('command')
                self.text = k.get('text')
                DummyButton.instances.append(self)

            def pack(self, *a, **k):
                pass

        class DummyLabel:
            instances = []

            def __init__(self, *a, **k):
                self.text = k.get('text')
                DummyLabel.instances.append(self)

            def pack(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

        class DummyEntry:
            instances = []

            def __init__(self, *a, **k):
                self.value = ""
                DummyEntry.instances.append(self)

            def pack(self, *a, **k):
                pass

            def get(self):
                return self.value

            def insert(self, index, value):
                self.value = value

            def delete(self, start, end=None):
                self.value = ""

            def bind(self, *a, **k):
                pass

        class DummyProgressbar:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        class DummyThread:
            def __init__(self, target, daemon=False):
                self.target = target

            def start(self):
                self.target()

            def is_alive(self):
                return False

        class DummyCheckbutton:
            def __init__(self, *a, **k):
                self.variable = k.get('variable')

            def pack(self, *a, **k):
                pass

        class DummyBooleanVar:
            def __init__(self, value=False):
                self.value = value

            def get(self):
                return self.value

            def set(self, val):
                self.value = val

        mp_fake = type('MP', (), {'unidad_medida': 'u'})()

        meta = {"proveedor": "Prov SA", "numero": "123", "fecha": "2024-05-01", "total": 1000}
        with patch('gui.compras_view.CompraDetalle', DummyCompraDetalle), \
             patch('gui.compras_view.registrar_compra_desde_imagen', return_value=(items_data, faltantes_data, meta)), \
             patch('gui.compras_view.solicitar_datos_materia_prima_masivo') as mock_solicitar, \
             patch('gui.compras_view.filedialog.askopenfilename', return_value='test.png'), \
             patch('gui.compras_view.messagebox'), \
             patch('gui.compras_view.listar_materias_primas', return_value=[]), \
             patch('gui.compras_view.obtener_materia_prima_por_id', return_value=mp_fake), \
             patch('gui.compras_view.DateEntry', DummyEntry), \
             patch('gui.compras_view.ttk.Label', DummyLabel), \
             patch('gui.compras_view.ttk.Progressbar', DummyProgressbar), \
             patch('gui.compras_view.ttk.Checkbutton', DummyCheckbutton), \
             patch('gui.compras_view.threading.Thread', DummyThread), \
             patch.multiple('gui.compras_view.tk', Toplevel=DummyToplevel, Frame=DummyFrame, Scrollbar=DummyScrollbar, Listbox=DummyListbox, Button=DummyButton, Label=DummyLabel, Entry=DummyEntry, BooleanVar=DummyBooleanVar):
            compras_view.mostrar_ventana_compras()
            DummyEntry.instances[0].insert(0, 'Proveedor')
            import_btn = next(b for b in DummyButton.instances if b.text == 'Importar desde imagen')
            import_btn.command()
            self.assertEqual(mock_solicitar.call_count, 0)
            self.assertTrue(any(b.text == 'Registrar faltantes' for b in DummyButton.instances))
            self.assertTrue(any(b.text == 'Crear materias primas nuevas' for b in DummyButton.instances))
            textos = [lbl.text for lbl in DummyLabel.instances if lbl.text]
            assert any("Proveedor: Prov SA" in t for t in textos)
            assert any("N°: 123" in t for t in textos)

    def test_crear_materias_primas_nuevas_invoca_dialogo(self):
        import gui.compras_view as compras_view

        items_data = [
            {"producto_id": "id1", "nombre_producto": "Item1", "cantidad": 1, "costo_unitario": 10},
        ]
        faltantes_data = [{"nombre_producto": "Falta1"}]

        class DummyCompraDetalle:
            def __init__(self, *a, **k):
                pass

        class DummyToplevel:
            def __init__(self, *a, **k):
                pass

            def title(self, *a):
                pass

            def geometry(self, *a):
                pass

            def attributes(self, *a, **k):
                pass

            def after(self, delay, func):
                func()

            def wait_window(self, *a):
                pass

            def pack(self, *a, **k):
                pass

            def destroy(self):
                pass

            def transient(self, *a):
                pass

            def grab_set(self):
                pass

        class DummyFrame:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

        class DummyScrollbar:
            def __init__(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

            def set(self, *a, **k):
                pass

        class DummyListbox:
            def __init__(self, *a, **k):
                self.items = []

            def pack(self, *a, **k):
                pass

            def delete(self, start, end=None):
                self.items = []

            def insert(self, index, item):
                self.items.append(item)

            def yview(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

            def bind(self, *a, **k):
                pass

            def size(self):
                return len(self.items)

            def curselection(self):
                return ()

            def selection_set(self, start, end=None):
                pass

            def selection_clear(self, start, end=None):
                pass

        class DummyButton:
            instances = []

            def __init__(self, *a, **k):
                self.command = k.get('command')
                self.text = k.get('text')
                DummyButton.instances.append(self)

            def pack(self, *a, **k):
                pass

        class DummyLabel:
            instances = []

            def __init__(self, *a, **k):
                self.text = k.get('text')
                DummyLabel.instances.append(self)

            def pack(self, *a, **k):
                pass

            def config(self, *a, **k):
                pass

        class DummyEntry:
            instances = []

            def __init__(self, *a, **k):
                self.value = ""
                DummyEntry.instances.append(self)

            def pack(self, *a, **k):
                pass

            def get(self):
                return self.value

            def insert(self, index, value):
                self.value = value

            def delete(self, start, end=None):
                self.value = ""

            def bind(self, *a, **k):
                pass

        class DummyProgressbar:
            def __init__(self, *a, **k):
                pass

            def pack(self, *a, **k):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        class DummyThread:
            def __init__(self, target, daemon=False):
                self.target = target

            def start(self):
                self.target()

            def is_alive(self):
                return False

        class DummyCheckbutton:
            def __init__(self, *a, **k):
                self.variable = k.get('variable')

            def pack(self, *a, **k):
                pass

        class DummyBooleanVar:
            def __init__(self, value=False):
                self.value = value

            def get(self):
                return self.value

            def set(self, val):
                self.value = val

        mp_fake = type('MP', (), {'unidad_medida': 'u'})()

        meta = {}
        with patch('gui.compras_view.CompraDetalle', DummyCompraDetalle), \
             patch('gui.compras_view.registrar_compra_desde_imagen', side_effect=[(items_data, faltantes_data, meta), (items_data, [], meta)]), \
             patch('gui.compras_view.registrar_materias_primas_faltantes', return_value=(['Falta1'], [])), \
             patch('gui.compras_view.solicitar_datos_materia_prima_masivo') as mock_solicitar, \
             patch('gui.compras_view.filedialog.askopenfilename', return_value='test.png'), \
             patch('gui.compras_view.messagebox'), \
             patch('gui.compras_view.listar_materias_primas', return_value=[]), \
             patch('gui.compras_view.obtener_materia_prima_por_id', return_value=mp_fake), \
             patch('gui.compras_view.DateEntry', DummyEntry), \
             patch('gui.compras_view.ttk.Label', DummyLabel), \
             patch('gui.compras_view.ttk.Progressbar', DummyProgressbar), \
             patch('gui.compras_view.ttk.Checkbutton', DummyCheckbutton), \
             patch('gui.compras_view.threading.Thread', DummyThread), \
             patch.multiple('gui.compras_view.tk', Toplevel=DummyToplevel, Frame=DummyFrame, Scrollbar=DummyScrollbar, Listbox=DummyListbox, Button=DummyButton, Label=DummyLabel, Entry=DummyEntry, BooleanVar=DummyBooleanVar):
            compras_view.mostrar_ventana_compras()
            DummyEntry.instances[0].insert(0, 'Proveedor')
            import_btn = next(b for b in DummyButton.instances if b.text == 'Importar desde imagen')
            import_btn.command()
            crear_btn = next(b for b in DummyButton.instances if b.text == 'Crear materias primas nuevas')
            crear_btn.command()
            mock_solicitar.assert_called_once()


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

