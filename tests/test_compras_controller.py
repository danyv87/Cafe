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

    @patch("controllers.compras_controller.actualizar_stock_materia_prima")
    def test_registrar_compra_con_fecha(self, mock_actualizar_stock):
        detalle = CompraDetalle(producto_id=2, nombre_producto="Azucar", cantidad=1, costo_unitario=5)
        fecha_custom = "2024-05-01 10:30:00"
        nueva_compra = compras_controller.registrar_compra("Proveedor Y", [detalle], fecha=fecha_custom)
        self.assertEqual(nueva_compra.fecha, fecha_custom)
        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 2)
        self.assertTrue(any(c.fecha == fecha_custom for c in compras))

    @patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
    def test_registrar_compra_desde_imagen(self, mock_parse):
        mock_parse.return_value = [
            {
                "producto_id": 3,
                "nombre_producto": "Leche",
                "cantidad": 2,
                "costo_unitario": 4,
            }
        ]

        items = compras_controller.registrar_compra_desde_imagen(
            "Proveedor Z", "dummy.jpg"
        )
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["nombre_producto"], "Leche")

        detalles = [CompraDetalle(**item) for item in items]

        # Aún no se guardó en el archivo
        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 1)

        with patch(
            "controllers.compras_controller.actualizar_stock_materia_prima"
        ) as mock_actualizar:
            compras_controller.registrar_compra(
                "Proveedor Z", detalles, fecha=""
            )
            mock_actualizar.assert_called_once()

        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 2)

    @patch(
        "controllers.compras_controller.receipt_parser.parse_receipt_image",
        side_effect=ConnectionError("fallo de red"),
    )
    def test_registrar_compra_desde_imagen_error_red(self, mock_parse):
        with self.assertRaises(ValueError) as ctx:
            compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")
        self.assertIn("conexión", str(ctx.exception).lower())

    @patch(
        "controllers.compras_controller.receipt_parser.parse_receipt_image",
        side_effect=ValueError("formato inválido"),
    )
    def test_registrar_compra_desde_imagen_error_parseo(self, mock_parse):
        with self.assertRaises(ValueError) as ctx:
            compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")
        self.assertEqual("formato inválido", str(ctx.exception))

    @patch("controllers.compras_controller.receipt_parser.parse_receipt_image")
    def test_registrar_compra_desde_imagen_datos_invalidos(self, mock_parse):
        mock_parse.return_value = [
            {
                "producto_id": 1,
                "nombre_producto": "",
                "cantidad": 0,
                "costo_unitario": 1,
            }
        ]
        with self.assertRaises(ValueError):
            compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")

    @patch(
        "controllers.compras_controller.receipt_parser.parse_receipt_image",
        side_effect=NotImplementedError("backend no disponible"),
    )
    def test_registrar_compra_desde_imagen_backend_no_disponible(self, mock_parse):
        with self.assertRaises(ValueError) as ctx:
            compras_controller.registrar_compra_desde_imagen("Proveedor", "img.jpg")
        # The controller should propagate the original message
        self.assertEqual("backend no disponible", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
