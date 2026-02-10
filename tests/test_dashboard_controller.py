import json

from controllers import dashboard_controller
from controllers import gastos_adicionales_controller
from controllers import materia_prima_controller
from controllers import recetas_controller
from controllers import tickets_controller


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def _configurar_paths(monkeypatch, tmp_path):
    tickets = tmp_path / "tickets.json"
    gastos = tmp_path / "gastos_adicionales.json"
    materias = tmp_path / "materias_primas.json"
    recetas = tmp_path / "recetas.json"

    monkeypatch.setattr(tickets_controller, "DATA_PATH", str(tickets))
    monkeypatch.setattr(gastos_adicionales_controller, "DATA_PATH", str(gastos))
    monkeypatch.setattr(materia_prima_controller, "DATA_PATH", str(materias))
    monkeypatch.setattr(recetas_controller, "DATA_PATH", str(recetas))
    materia_prima_controller.clear_materias_cache()

    return tickets, gastos, materias, recetas


def test_meses_disponibles_dashboard(monkeypatch, tmp_path):
    tickets, gastos, materias, recetas = _configurar_paths(monkeypatch, tmp_path)

    _write(
        tickets,
        [
            {"id": "t1", "fecha": "2025-06-10 10:00:00", "cliente": "Ana", "items_venta": [], "total": 0},
            {"id": "t2", "fecha": "2025-07-01 11:00:00", "cliente": "Bob", "items_venta": [], "total": 0},
        ],
    )
    _write(
        gastos,
        [{"id": "g1", "nombre": "Luz", "monto": 1000, "fecha": "2025-08-02 09:00:00", "descripcion": ""}],
    )
    _write(materias, [])
    _write(recetas, [])

    assert dashboard_controller.meses_disponibles_dashboard() == ["2025-06", "2025-07", "2025-08"]


def test_calcular_metricas_dashboard_mensual(monkeypatch, tmp_path):
    tickets, gastos, materias, recetas = _configurar_paths(monkeypatch, tmp_path)

    _write(
        tickets,
        [
            {
                "id": "t1",
                "fecha": "2025-06-10 10:00:00",
                "cliente": "Ana",
                "items_venta": [
                    {
                        "fecha_item": "2025-06-10 10:00:00",
                        "producto_id": "p1",
                        "nombre_producto": "Producto 1",
                        "cantidad": 2,
                        "precio_unitario": 10,
                        "total": 20,
                    }
                ],
                "total": 20,
            },
            {
                "id": "t2",
                "fecha": "2025-06-11 11:00:00",
                "cliente": "Bob",
                "items_venta": [
                    {
                        "fecha_item": "2025-06-11 11:00:00",
                        "producto_id": "p2",
                        "nombre_producto": "Producto 2",
                        "cantidad": 1,
                        "precio_unitario": 30,
                        "total": 30,
                    }
                ],
                "total": 30,
            },
            {
                "id": "t3",
                "fecha": "2025-07-01 12:00:00",
                "cliente": "Caro",
                "items_venta": [
                    {
                        "fecha_item": "2025-07-01 12:00:00",
                        "producto_id": "p1",
                        "nombre_producto": "Producto 1",
                        "cantidad": 1,
                        "precio_unitario": 10,
                        "total": 10,
                    }
                ],
                "total": 10,
            },
        ],
    )
    _write(
        gastos,
        [
            {"id": "g1", "nombre": "Luz", "monto": 5, "fecha": "2025-06-12 09:00:00", "descripcion": ""},
            {"id": "g2", "nombre": "Gas", "monto": 7, "fecha": "2025-07-12 09:00:00", "descripcion": ""},
        ],
    )
    _write(
        materias,
        [
            {"id": "m1", "nombre": "Harina", "unidad_medida": "kg", "costo_unitario": 4, "stock": 0, "stock_minimo": 0},
            {"id": "m2", "nombre": "Leche", "unidad_medida": "litros", "costo_unitario": 12, "stock": 0, "stock_minimo": 0},
        ],
    )
    _write(
        recetas,
        [
            {
                "id": "r1",
                "producto_id": "p1",
                "nombre_producto": "Producto 1",
                "ingredientes": [{"materia_prima_id": "m1", "cantidad_necesaria": 1}],
                "rendimiento": None,
                "procedimiento": None,
            },
            {
                "id": "r2",
                "producto_id": "p2",
                "nombre_producto": "Producto 2",
                "ingredientes": [{"materia_prima_id": "m2", "cantidad_necesaria": 1}],
                "rendimiento": None,
                "procedimiento": None,
            },
        ],
    )

    metricas = dashboard_controller.calcular_metricas_dashboard_mensual("2025-06")

    assert metricas.ventas_totales == 50
    assert metricas.costos_produccion == 20
    assert metricas.gastos_adicionales == 5
    assert metricas.resultado_mes == 25
    assert metricas.unidades_vendidas == 3
    assert metricas.dias_operativos == 2
    assert metricas.ticket_promedio == 25
    assert metricas.ventas_diarias_promedio == 25
    assert metricas.top_productos[0]["producto_id"] == "p2"
    assert metricas.productos_problema[0]["producto_id"] == "p1"
