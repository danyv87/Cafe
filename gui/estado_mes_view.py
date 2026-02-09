from datetime import datetime
import tkinter as tk
from tkinter import ttk

from controllers.compras_controller import listar_compras
from controllers.gastos_adicionales_controller import listar_gastos_adicionales
from controllers.planes_venta_controller import cargar_planes_venta
from controllers.tickets_controller import listar_tickets


def _formatear_moneda(valor: float) -> str:
    return f"Gs {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _obtener_periodo_actual() -> str:
    return datetime.now().strftime("%Y-%m")


def _parse_fecha(fecha):
    if isinstance(fecha, datetime):
        return fecha
    if isinstance(fecha, str):
        fecha = fecha[:19]
        for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(fecha, formato)
            except ValueError:
                continue
    return None


def _obtener_plan_ventas_actual():
    planes = cargar_planes_venta()
    if not planes:
        return None
    plan_ordenado = sorted(
        planes,
        key=lambda plan: _parse_fecha(plan.get("actualizado")) or datetime.min,
        reverse=True,
    )
    return plan_ordenado[0]


def agregar_tab_estado_mes(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con el estado del mes."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Estado del Mes")

    periodo_actual = _obtener_periodo_actual()
    ttk.Label(
        frame,
        text=f"Estado del mes: {periodo_actual}",
        font=("Helvetica", 16, "bold"),
    ).pack(pady=15)

    frame_info = ttk.Frame(frame)
    frame_info.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    tickets = listar_tickets()
    compras = listar_compras()
    gastos = listar_gastos_adicionales()

    total_ventas = 0.0
    total_compras = 0.0
    total_gastos = 0.0
    tickets_mes = 0
    compras_mes = 0
    ventas_por_producto = {}

    for ticket in tickets:
        fecha_ticket = _parse_fecha(ticket.fecha)
        if not fecha_ticket or fecha_ticket.strftime("%Y-%m") != periodo_actual:
            continue
        tickets_mes += 1
        total_ventas += ticket.total
        for item in ticket.items_venta:
            ventas_por_producto[item.nombre_producto] = (
                ventas_por_producto.get(item.nombre_producto, 0.0) + item.total
            )

    for compra in compras:
        fecha_compra = _parse_fecha(compra.fecha)
        if not fecha_compra or fecha_compra.strftime("%Y-%m") != periodo_actual:
            continue
        compras_mes += 1
        total_compras += compra.total

    for gasto in gastos:
        fecha_gasto = _parse_fecha(gasto.fecha)
        if not fecha_gasto or fecha_gasto.strftime("%Y-%m") != periodo_actual:
            continue
        total_gastos += gasto.monto

    resultado_neto = total_ventas - total_compras - total_gastos
    promedio_ticket = total_ventas / tickets_mes if tickets_mes else 0.0
    producto_top = max(ventas_por_producto.items(), key=lambda item: item[1], default=None)
    plan_actual = _obtener_plan_ventas_actual()
    ventas_plan = 0.0
    nombre_plan = None
    if plan_actual:
        nombre_plan = plan_actual.get("nombre", "").strip() or "Plan sin nombre"
        for item in plan_actual.get("items", []):
            unidades = item.get("unidades", item.get("unidades_previstas", 0)) or 0
            precio = item.get("precio", item.get("precio_venta_unitario", 0)) or 0
            try:
                ventas_plan += float(unidades) * float(precio)
            except (TypeError, ValueError):
                continue
    cumplimiento_plan = (total_ventas / ventas_plan * 100) if ventas_plan > 0 else None
    diferencia_plan = total_ventas - ventas_plan if ventas_plan > 0 else None

    datos = [
        ("Ventas del mes", _formatear_moneda(total_ventas)),
        ("Compras del mes", _formatear_moneda(total_compras)),
        ("Gastos adicionales del mes", _formatear_moneda(total_gastos)),
        ("Resultado neto del mes", _formatear_moneda(resultado_neto)),
        ("Tickets emitidos", f"{tickets_mes} tickets"),
        ("Compras registradas", f"{compras_mes} compras"),
        ("Promedio por ticket", _formatear_moneda(promedio_ticket)),
    ]

    if producto_top:
        datos.append(
            (
                "Producto más vendido del mes",
                f"{producto_top[0]} ({_formatear_moneda(producto_top[1])})",
            )
        )
    else:
        datos.append(("Producto más vendido del mes", "N/D"))

    if ventas_plan > 0:
        cumplimiento_fmt = f"{cumplimiento_plan:.2f}%".replace(".", ",") if cumplimiento_plan is not None else "N/D"
        datos.extend(
            [
                ("Plan de ventas activo", nombre_plan or "N/D"),
                ("Ventas planificadas", _formatear_moneda(ventas_plan)),
                ("Diferencia vs plan", _formatear_moneda(diferencia_plan or 0.0)),
                ("Cumplimiento del plan", cumplimiento_fmt),
            ]
        )
    else:
        datos.append(("Plan de ventas activo", nombre_plan or "N/D"))
        datos.append(("Ventas planificadas", "N/D"))
        datos.append(("Diferencia vs plan", "N/D"))
        datos.append(("Cumplimiento del plan", "N/D"))

    for fila, (etiqueta, valor) in enumerate(datos):
        ttk.Label(frame_info, text=f"{etiqueta}:", font=("Helvetica", 11, "bold")).grid(
            row=fila, column=0, sticky="w", pady=4, padx=5
        )
        ttk.Label(frame_info, text=valor, font=("Helvetica", 11)).grid(
            row=fila, column=1, sticky="w", pady=4, padx=5
        )

    frame_info.columnconfigure(1, weight=1)
