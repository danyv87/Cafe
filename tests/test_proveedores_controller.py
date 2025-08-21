import os
import json
import tempfile
import unittest

from controllers import proveedores_controller

class TestProveedoresController(unittest.TestCase):
    def setUp(self):
        self.orig_path = proveedores_controller.DATA_PATH
        self.tmp = tempfile.TemporaryDirectory()
        proveedores_controller.DATA_PATH = os.path.join(self.tmp.name, "proveedores.json")
        with open(proveedores_controller.DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

    def tearDown(self):
        proveedores_controller.DATA_PATH = self.orig_path
        self.tmp.cleanup()

    def test_agregar_y_editar_proveedor(self):
        prov = proveedores_controller.agregar_proveedor("Prov1", "c")
        self.assertEqual(prov.nombre, "Prov1")
        lista = proveedores_controller.listar_proveedores()
        self.assertEqual(len(lista), 1)
        editado = proveedores_controller.editar_proveedor(prov.id, "Nuevo", "x")
        self.assertEqual(editado.nombre, "Nuevo")
        self.assertEqual(editado.contacto, "x")

if __name__ == "__main__":
    unittest.main()
