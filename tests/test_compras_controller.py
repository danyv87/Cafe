import os
import json
import tempfile
import unittest
from unittest.mock import patch

from controllers import compras_controller
from models.compra import Compra
from models.compra_detalle import CompraDetalle

class TestCargarCompras(unittest.TestCase):
    def setUp(self):
        # Preserve original DATA_PATH to restore later
        self.original_data_path = compras_controller.DATA_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "compras.json")

        # Prepare a sample Compra and write it to the temporary JSON file
        detalle = CompraDetalle(producto_id=1, nombre_producto="Cafe", cantidad=2, costo_unitario=10)
        compra = Compra(proveedor="Proveedor X", items_compra=[detalle])
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump([compra.to_dict()], f)

        # Point the controller to the temporary file
        compras_controller.DATA_PATH = self.temp_file

    def tearDown(self):
        compras_controller.DATA_PATH = self.original_data_path
        self.temp_dir.cleanup()

    def test_cargar_compras(self):
        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 1)
        compra = compras[0]
        self.assertEqual(compra.proveedor, "Proveedor X")
        self.assertEqual(len(compra.items_compra), 1)
        self.assertEqual(compra.items_compra[0].nombre_producto, "Cafe")
        # Ensure the controller's path points to compras.json
        self.assertEqual(os.path.basename(compras_controller.DATA_PATH), "compras.json")

    @patch("controllers.compras_controller.exportar_compras_excel")
    @patch("controllers.compras_controller.actualizar_stock_materia_prima")
    def test_registrar_compra_con_fecha(self, mock_actualizar_stock, mock_exportar_excel):
        detalle = CompraDetalle(producto_id=2, nombre_producto="Azucar", cantidad=1, costo_unitario=5)
        fecha_custom = "2024-05-01 10:30:00"
        nueva_compra = compras_controller.registrar_compra("Proveedor Y", [detalle], fecha=fecha_custom)
        self.assertEqual(nueva_compra.fecha, fecha_custom)
        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 2)
        self.assertTrue(any(c.fecha == fecha_custom for c in compras))

    @patch("controllers.compras_controller.exportar_compras_excel")
    @patch("controllers.compras_controller.actualizar_stock_materia_prima")
    @patch("controllers.compras_controller.validar_items")
    @patch("controllers.compras_controller.gpt_receipt_parser.parse_receipt")
    def test_registrar_compra_desde_imagen(self, mock_parse, mock_validar, mock_actualizar_stock, mock_exportar_excel):
        mock_parse.return_value = [
            {"producto_id": 1, "nombre_producto": "Cafe", "cantidad": 1, "costo_unitario": 10},
            {"producto_id": 2, "nombre_producto": "Azucar", "cantidad": 2, "costo_unitario": 5},
        ]
        mock_validar.return_value = True
        nueva_compra = compras_controller.registrar_compra_desde_imagen("Proveedor Img", "ruta.png")
        self.assertEqual(len(nueva_compra.items_compra), 2)
        self.assertEqual(nueva_compra.total, 20)

if __name__ == "__main__":
    unittest.main()
