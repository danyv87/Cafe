from __future__ import annotations

import calendar
import datetime as dt
from collections import defaultdict
from dataclasses import dataclass

from controllers.gastos_adicionales_controller import listar_gastos_adicionales
from controllers.materia_prima_controller import obtener_materia_prima_por_id
from controllers.recetas_controller import obtener_receta_por_producto_id
from controllers.tickets_controller import cargar_tickets


@dataclass
class DashboardMetricas:
    mes: str
    ventas_totales: float
    costos_produccion: float
    gastos_adicionales: float
    resultado_mes: float
    punto_equilibrio: float
    unidades_vendidas: int
    ticket_promedio: float
    ventas_diarias_promedio: float
    dias_operativos: int
    costos_produccion_pendientes: bool
    top_productos: list[dict]
    productos_problema: list[dict]


def _parse_fecha(fecha: str | dt.datetime | None) -> dt.datetime | None:
    if not fecha:
        return None
    if isinstance(fecha, dt.datetime):
        return fecha
    if isinstance(fecha, str):
        fecha_limpia = fecha[:19]
        formatos = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
        for fmt in formatos:
            try:
                return dt.datetime.strptime(fecha_limpia, fmt)
            except ValueError:
                continue
    return None


def _costo_unitario_producto(producto_id: str) -> float:
    receta = obtener_receta_por_producto_id(producto_id)
    if not receta:
        return 0.0

    costo_lote = 0.0
    for ingrediente in receta.ingredientes:
        materia = obtener_materia_prima_por_id(ingrediente["materia_prima_id"])
        if not materia:
            continue
        costo_lote += float(ingrediente.get("cantidad_necesaria", 0) or 0) * float(materia.costo_unitario or 0)

    rendimiento = getattr(receta, "rendimiento", None)
    if rendimiento and rendimiento > 0:
        return costo_lote / rendimiento
    return costo_lote


def meses_disponibles_dashboard() -> list[str]:
    meses = set()
    for ticket in cargar_tickets():
        fecha = _parse_fecha(getattr(ticket, "fecha", None))
        if fecha:
            meses.add(fecha.strftime("%Y-%m"))

    for gasto in listar_gastos_adicionales():
        fecha = _parse_fecha(getattr(gasto, "fecha", None))
        if fecha:
            meses.add(fecha.strftime("%Y-%m"))

    return sorted(meses)


def _rango_mes(mes: str) -> tuple[dt.datetime, dt.datetime]:
    year, month = [int(p) for p in mes.split("-")]
    ultimo_dia = calendar.monthrange(year, month)[1]
    inicio = dt.datetime(year, month, 1, 0, 0, 0)
    fin = dt.datetime(year, month, ultimo_dia, 23, 59, 59)
    return inicio, fin


def calcular_metricas_dashboard_mensual(mes: str) -> DashboardMetricas:
    inicio, fin = _rango_mes(mes)

    ventas_totales = 0.0
    costos_produccion = 0.0
    unidades_vendidas = 0
    dias_con_ventas = set()

    ventas_por_producto = defaultdict(float)
    unidades_por_producto = defaultdict(int)
    margen_por_producto = defaultdict(float)
    costo_pendiente_por_producto = defaultdict(bool)
    nombres_por_producto = {}

    for ticket in cargar_tickets():
        fecha_ticket = _parse_fecha(getattr(ticket, "fecha", None))
        if not fecha_ticket or not (inicio <= fecha_ticket <= fin):
            continue

        dias_con_ventas.add(fecha_ticket.date())
        ventas_totales += float(ticket.total or 0)

        for item in ticket.items_venta:
            cantidad = int(item.cantidad or 0)
            total_item = float(item.total or 0)
            producto_id = item.producto_id
            if producto_id and producto_id not in nombres_por_producto:
                nombres_por_producto[producto_id] = getattr(item, "nombre_producto", "")
            unidades_vendidas += cantidad
            ventas_por_producto[producto_id] += total_item
            unidades_por_producto[producto_id] += cantidad

            costo_unitario = _costo_unitario_producto(producto_id)
            if cantidad > 0 and costo_unitario <= 0:
                costo_pendiente_por_producto[producto_id] = True
            costo_item = costo_unitario * cantidad
            costos_produccion += costo_item
            margen_por_producto[producto_id] += total_item - costo_item

    gastos_adicionales = 0.0
    for gasto in listar_gastos_adicionales():
        fecha_gasto = _parse_fecha(getattr(gasto, "fecha", None))
        if fecha_gasto and inicio <= fecha_gasto <= fin:
            gastos_adicionales += float(gasto.monto or 0)

    resultado_mes = ventas_totales - costos_produccion - gastos_adicionales

    ticket_promedio = 0.0
    total_tickets_mes = sum(
        1
        for t in cargar_tickets()
        if (fecha_t := _parse_fecha(getattr(t, "fecha", None))) and inicio <= fecha_t <= fin
    )
    if total_tickets_mes > 0:
        ticket_promedio = ventas_totales / total_tickets_mes

    dias_operativos = len(dias_con_ventas)
    ventas_diarias_promedio = ventas_totales / dias_operativos if dias_operativos > 0 else 0.0

    punto_equilibrio = costos_produccion + gastos_adicionales

    ranking = []
    for producto_id, total_vendido in ventas_por_producto.items():
        margen_total = margen_por_producto[producto_id]
        margen_pct = (margen_total / total_vendido * 100) if total_vendido > 0 else 0.0
        ranking.append(
            {
                "producto_id": producto_id,
                "nombre_producto": nombres_por_producto.get(producto_id, ""),
                "ventas": total_vendido,
                "margen_pct": margen_pct,
                "margen_total": margen_total,
                "unidades": unidades_por_producto[producto_id],
                "costo_pendiente": costo_pendiente_por_producto[producto_id],
            }
        )

    top_productos = sorted(ranking, key=lambda x: x["margen_total"], reverse=True)[:3]
    productos_problema = sorted(ranking, key=lambda x: x["margen_total"])[:3]

    return DashboardMetricas(
        mes=mes,
        ventas_totales=ventas_totales,
        costos_produccion=costos_produccion,
        gastos_adicionales=gastos_adicionales,
        resultado_mes=resultado_mes,
        punto_equilibrio=punto_equilibrio,
        unidades_vendidas=unidades_vendidas,
        ticket_promedio=ticket_promedio,
        ventas_diarias_promedio=ventas_diarias_promedio,
        dias_operativos=dias_operativos,
        costos_produccion_pendientes=any(costo_pendiente_por_producto.values()),
        top_productos=top_productos,
        productos_problema=productos_problema,
    )
