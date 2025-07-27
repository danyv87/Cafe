import json
import os
import tempfile
import unittest
from unittest import mock

from models.compra_detalle import CompraDetalle
from models.compra import Compra
import controllers.compras_controller as cc

class TestComprasController(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.compras_path = os.path.join(self.tmpdir.name, "compras.json")
        with open(self.compras_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        self.patch_data_path = mock.patch.object(cc, "DATA_PATH", self.compras_path)
        self.patch_data_path.start()

    def tearDown(self):
        self.patch_data_path.stop()
        self.tmpdir.cleanup()

    def write_compras(self, compras):
        with open(self.compras_path, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in compras], f)

    def test_obtener_compras_por_semana(self):
        # create compras in two different weeks
        item1 = CompraDetalle("mp1", "Azucar", 2, 500)
        compra1 = Compra("Prov1", [item1], fecha="2023-01-02 10:00:00")
        compra2 = Compra("Prov2", [item1], fecha="2023-01-07 10:00:00")
        compra3 = Compra("Prov3", [item1], fecha="2023-01-10 10:00:00")
        self.write_compras([compra1, compra2, compra3])

        result = cc.obtener_compras_por_semana()
        expected = [
            ("2023-W01", "Gs 2.000"),
            ("2023-W02", "Gs 1.000"),
        ]
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
