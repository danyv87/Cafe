import json
import os
import tempfile
import unittest
from unittest import mock

from models.venta_detalle import VentaDetalle
import controllers.tickets_controller as tc

class TestTicketsController(unittest.TestCase):
    def setUp(self):
        # create temporary file for tickets
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tickets_path = os.path.join(self.tmpdir.name, "tickets.json")
        with open(self.tickets_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        self.patch_data_path = mock.patch.object(tc, "DATA_PATH", self.tickets_path)
        self.patch_data_path.start()
        # patch external dependencies used inside registrar_ticket
        self.listar_mp = mock.patch("controllers.tickets_controller.listar_materias_primas", return_value=[])
        self.guardar_mp = mock.patch("controllers.tickets_controller.guardar_materias_primas")
        self.obtener_receta = mock.patch("controllers.tickets_controller.obtener_receta_por_producto_id", return_value=None)
        self.listar_mp.start()
        self.guardar_mp.start()
        self.obtener_receta.start()

    def tearDown(self):
        self.patch_data_path.stop()
        self.listar_mp.stop()
        self.guardar_mp.stop()
        self.obtener_receta.stop()
        self.tmpdir.cleanup()

    def test_registrar_y_listar_ticket(self):
        item = VentaDetalle(producto_id="p1", nombre_producto="Cafe", cantidad=2, precio_unitario=1000)
        ticket = tc.registrar_ticket("Cliente", [item])
        self.assertEqual(ticket.cliente, "Cliente")
        self.assertEqual(ticket.total, 2000)

        # listar_tickets debe devolver el ticket recien guardado
        tickets = tc.listar_tickets()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].cliente, "Cliente")
        self.assertEqual(tickets[0].total, 2000)

    def test_registrar_ticket_cliente_vacio(self):
        item = VentaDetalle(producto_id="p1", nombre_producto="Cafe", cantidad=1, precio_unitario=500)
        with self.assertRaises(ValueError):
            tc.registrar_ticket("", [item])

if __name__ == "__main__":
    unittest.main()
