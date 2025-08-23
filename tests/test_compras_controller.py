import os
import json
import tempfile
import unittest
from unittest.mock import patch

from controllers import compras_controller
from controllers import materia_prima_controller as mp_controller
from models.compra import Compra
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor

class TestCargarCompras(unittest.TestCase):
    def setUp(self):
        # Preserve original DATA_PATH to restore later
        self.original_data_path = compras_controller.DATA_PATH
        self.original_mp_path = mp_controller.DATA_PATH

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "compras.json")
        self.temp_mp_file = os.path.join(self.temp_dir.name, "materias.json")

        # Create empty materias file and configure controller
        with open(self.temp_mp_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        mp_controller.DATA_PATH = self.temp_mp_file
        mp_controller.clear_materias_cache()

        # Add a materia prima for testing
        self.materia = mp_controller.agregar_materia_prima("Cafe", "kg", 10, 10)

        # Prepare a sample Compra and write it to the temporary JSON file
        detalle = CompraDetalle(
            producto_id=self.materia.id,
            nombre_producto="Cafe",
            cantidad=2,
            costo_unitario=10,
        )
        self.proveedor = Proveedor("Proveedor X", "c")
        compra = Compra(proveedor_id=self.proveedor.id, items_compra=[detalle])
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump([compra.to_dict()], f)

        # Point the controller to the temporary file
        compras_controller.DATA_PATH = self.temp_file

    def tearDown(self):
        compras_controller.DATA_PATH = self.original_data_path
        mp_controller.DATA_PATH = self.original_mp_path
        mp_controller.clear_materias_cache()
        self.temp_dir.cleanup()

    def test_cargar_compras(self):
        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 1)
        compra = compras[0]
        self.assertEqual(compra.proveedor_id, self.proveedor.id)
        self.assertEqual(len(compra.items_compra), 1)
        self.assertEqual(compra.items_compra[0].nombre_producto, "Cafe")
        # Ensure the controller's path points to compras.json
        self.assertEqual(os.path.basename(compras_controller.DATA_PATH), "compras.json")

    @patch("controllers.compras_controller.actualizar_stock_materia_prima")
    def test_registrar_compra_con_fecha(self, mock_actualizar_stock):
        detalle = CompraDetalle(producto_id=2, nombre_producto="Azucar", cantidad=1, costo_unitario=5)
        fecha_custom = "2024-05-01 10:30:00"
        proveedor_y = Proveedor("Proveedor Y")
        nueva_compra = compras_controller.registrar_compra(proveedor_y, [detalle], fecha=fecha_custom)
        self.assertEqual(nueva_compra.fecha, fecha_custom)
        compras = compras_controller.cargar_compras()
        self.assertEqual(len(compras), 2)
        self.assertTrue(any(c.fecha == fecha_custom for c in compras))


    def test_eliminar_compra_actualiza_stock_y_archivo(self):
        # Registrar una compra adicional para eliminar luego
        detalle = CompraDetalle(
            producto_id=self.materia.id,
            nombre_producto="Cafe",
            cantidad=3,
            costo_unitario=10,
        )
        proveedor = Proveedor("Proveedor Extra")
        compra = compras_controller.registrar_compra(proveedor, [detalle])

        # Verificar que el stock aumentó
        mp = mp_controller.listar_materias_primas()[0]
        self.assertEqual(mp.stock, 13)  # 10 iniciales + 3 de la compra

        # Eliminar la compra
        compras_controller.eliminar_compra(compra.id)

        # Se removió del archivo
        compras = compras_controller.cargar_compras()
        self.assertFalse(any(c.id == compra.id for c in compras))

        # El stock volvió al valor original
        mp = mp_controller.listar_materias_primas()[0]
        self.assertEqual(mp.stock, 10)

    def test_eliminar_compra_id_inexistente(self):
        with self.assertRaises(ValueError):
            compras_controller.eliminar_compra("id-que-no-existe")

if __name__ == "__main__":
    unittest.main()
