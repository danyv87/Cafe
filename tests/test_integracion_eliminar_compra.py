import os
import json
import tempfile
import unittest
from unittest.mock import patch

from controllers import compras_controller
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor


class TestIntegracionEliminarCompra(unittest.TestCase):
    def setUp(self):
        self.original_path = compras_controller.DATA_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "compras.json")
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        compras_controller.DATA_PATH = self.temp_file

    def tearDown(self):
        compras_controller.DATA_PATH = self.original_path
        self.temp_dir.cleanup()

    @patch("controllers.compras_controller.actualizar_stock_materia_prima")
    def test_registro_y_eliminacion_actualiza_reportes(self, mock_actualizar):
        detalle = CompraDetalle(producto_id=1, nombre_producto="Cafe", cantidad=2, costo_unitario=10)
        proveedor = Proveedor("Proveedor X")
        compra = compras_controller.registrar_compra(
            proveedor, [detalle], fecha="2024-05-01 10:30:00"
        )

        compras_mes = compras_controller.obtener_compras_por_mes()
        self.assertEqual(len(compras_mes), 1)
        self.assertEqual(compras_mes[0][0], "2024-05")

        with patch("controllers.compras_controller.exportar_compras_excel") as mock_export:
            compras_controller.eliminar_compra(compra.id)
            self.assertGreaterEqual(mock_export.call_count, 1)

        self.assertEqual(compras_controller.obtener_compras_por_mes(), [])


if __name__ == "__main__":
    unittest.main()

