import os
import json
import tempfile
import unittest

from controllers import materia_prima_controller as mp_controller


class TestMateriaPrimaController(unittest.TestCase):
    def setUp(self):
        self.original_path = mp_controller.DATA_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "materias.json")
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        mp_controller.DATA_PATH = self.temp_file

    def tearDown(self):
        mp_controller.DATA_PATH = self.original_path
        self.temp_dir.cleanup()

    def test_validar_materia_prima_con_stock_minimo(self):
        valido, _ = mp_controller.validar_materia_prima("Azucar", "kg", 10, 5, 3)
        self.assertTrue(valido)
        valido, _ = mp_controller.validar_materia_prima("Azucar", "kg", 10, 2, 3)
        self.assertFalse(valido)

    def test_agregar_y_listar_materia_prima_con_stock_minimo(self):
        mp_controller.agregar_materia_prima("Cafe", "kg", 10, 5, 2)
        materias = mp_controller.listar_materias_primas()
        self.assertEqual(len(materias), 1)
        self.assertEqual(materias[0].stock_minimo, 2)

    def test_materias_con_stock_bajo(self):
        mp_controller.agregar_materia_prima("Cafe", "kg", 10, 1, 1)
        mp_controller.agregar_materia_prima("Azucar", "kg", 10, 2, 2)
        bajas = mp_controller.materias_con_stock_bajo()
        self.assertEqual(len(bajas), 2)
        nombres = sorted(mp.nombre for mp in bajas)
        self.assertEqual(nombres, ["Azucar", "Cafe"])


if __name__ == "__main__":
    unittest.main()
