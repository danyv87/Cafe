import unittest
from unittest.mock import patch

from controllers import tickets_controller, gastos_adicionales_controller, reportes_financieros
from models.ticket import Ticket
from models.venta_detalle import VentaDetalle
from models.gasto_adicional import GastoAdicional
from models.receta import Receta
from models.materia_prima import MateriaPrima


class TestReportesFinancieros(unittest.TestCase):
    def setUp(self):
        self.ticket1 = Ticket(
            cliente="A",
            items_venta=[VentaDetalle("p1", "Prod1", 2, 10)],
            fecha="2024-01-01 10:00:00",
        )
        self.ticket2 = Ticket(
            cliente="B",
            items_venta=[VentaDetalle("p2", "Prod2", 1, 5)],
            fecha="2024-02-01 10:00:00",
        )
        self.gasto1 = GastoAdicional("Luz", 5, fecha="2024-01-02 12:00:00")
        self.gasto2 = GastoAdicional("Agua", 3, fecha="2024-03-01 12:00:00")

    @patch("controllers.tickets_controller.cargar_tickets")
    def test_total_vendido_periodo(self, mock_cargar):
        mock_cargar.return_value = [self.ticket1, self.ticket2]
        total = tickets_controller.total_vendido_periodo("2024-01-01", "2024-01-31")
        self.assertEqual(total, 20)

    @patch("controllers.gastos_adicionales_controller.cargar_gastos_adicionales")
    def test_total_gastos_periodo(self, mock_cargar):
        mock_cargar.return_value = [self.gasto1, self.gasto2]
        total = gastos_adicionales_controller.total_gastos_periodo("2024-01-01", "2024-01-31")
        self.assertEqual(total, 5)

    @patch("controllers.reportes_financieros.obtener_materia_prima_por_id")
    @patch("controllers.reportes_financieros.obtener_receta_por_producto_id")
    @patch("controllers.reportes_financieros.cargar_tickets")
    @patch("controllers.tickets_controller.cargar_tickets")
    @patch("controllers.gastos_adicionales_controller.cargar_gastos_adicionales")
    def test_estado_resultado(self, mock_gastos, mock_tickets_tc, mock_tickets_rf, mock_receta, mock_mp):
        mock_tickets_tc.return_value = [self.ticket1]
        mock_tickets_rf.return_value = [self.ticket1]
        mock_gastos.return_value = [self.gasto1]
        receta = Receta(
            producto_id="p1",
            nombre_producto="Prod1",
            ingredientes=[{"materia_prima_id": "m1", "nombre_materia_prima": "Harina", "cantidad_necesaria": 2}],
            rendimiento=1,
        )
        mock_receta.return_value = receta
        mp = MateriaPrima(nombre="Harina", unidad_medida="kg", costo_unitario=1, stock=10, id="m1")
        mock_mp.return_value = mp
        res = reportes_financieros.estado_resultado("2024-01-01", "2024-01-31")
        self.assertEqual(res["ventas"], 20)
        self.assertEqual(res["costos_produccion"], 4)
        self.assertEqual(res["gastos_adicionales"], 5)
        self.assertEqual(res["resultado_neto"], 11)


if __name__ == "__main__":
    unittest.main()
