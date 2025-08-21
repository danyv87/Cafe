import os
import json
import tempfile
import unittest

from controllers import tickets_controller
from models.ticket import Ticket
from models.venta_detalle import VentaDetalle


class TestObtenerVentasPorProducto(unittest.TestCase):
    def setUp(self):
        self.original_data_path = tickets_controller.DATA_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "tickets.json")

        # Crear tickets de ejemplo
        item1 = VentaDetalle(producto_id=1, nombre_producto="Cafe", cantidad=2, precio_unitario=10)
        item2 = VentaDetalle(producto_id=2, nombre_producto="Te", cantidad=1, precio_unitario=5)
        ticket1 = Ticket(cliente="Alice", items_venta=[item1, item2])

        item3 = VentaDetalle(producto_id=1, nombre_producto="Cafe", cantidad=1, precio_unitario=10)
        ticket2 = Ticket(cliente="Bob", items_venta=[item3])

        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump([ticket1.to_dict(), ticket2.to_dict()], f)

        tickets_controller.DATA_PATH = self.temp_file

    def tearDown(self):
        tickets_controller.DATA_PATH = self.original_data_path
        self.temp_dir.cleanup()

    def test_obtener_ventas_por_producto(self):
        ventas = tickets_controller.obtener_ventas_por_producto()
        self.assertEqual(ventas, {1: 30.0, 2: 5.0})


if __name__ == "__main__":
    unittest.main()
