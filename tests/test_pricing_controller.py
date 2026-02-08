import pytest

from controllers.pricing_controller import (
    PlanVentaItem,
    calcular_costo_fijo_unitario_proporcional,
)


def test_calcular_costo_fijo_unitario_proporcional_reparte_por_valor():
    plan = [
        PlanVentaItem(producto_id="p1", unidades_previstas=10, precio_venta_unitario=10000),
        PlanVentaItem(producto_id="p2", unidades_previstas=10, precio_venta_unitario=100000),
    ]

    costos_fijos_unitarios = calcular_costo_fijo_unitario_proporcional(110000, plan)

    assert pytest.approx(costos_fijos_unitarios["p1"], rel=1e-6) == 1000
    assert pytest.approx(costos_fijos_unitarios["p2"], rel=1e-6) == 10000


def test_calcular_costo_fijo_unitario_proporcional_valida_plan():
    with pytest.raises(ValueError):
        calcular_costo_fijo_unitario_proporcional(1000, [])
