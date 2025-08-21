import datetime
from controllers.tickets_controller import total_vendido_periodo, cargar_tickets
from controllers.gastos_adicionales_controller import total_gastos_periodo
from controllers.recetas_controller import obtener_receta_por_producto_id
from controllers.materia_prima_controller import obtener_materia_prima_por_id


def _parse_fecha(fecha):
    if isinstance(fecha, datetime.datetime):
        return fecha
    if isinstance(fecha, str):
        fecha = fecha[:19]
        try:
            if len(fecha) == 10:
                return datetime.datetime.strptime(fecha, "%Y-%m-%d")
            return datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'.")
    raise TypeError("La fecha debe ser un string o datetime.")


def _costo_produccion_periodo(inicio, fin):
    inicio_dt = _parse_fecha(inicio)
    fin_dt = _parse_fecha(fin)
    total = 0.0
    for ticket in cargar_tickets():
        try:
            fecha_ticket = _parse_fecha(ticket.fecha)
        except Exception:
            continue
        if inicio_dt <= fecha_ticket <= fin_dt:
            for item in ticket.items_venta:
                receta = obtener_receta_por_producto_id(item.producto_id)
                if not receta:
                    continue
                rendimiento = getattr(receta, 'rendimiento', None)
                for ingrediente in receta.ingredientes:
                    mp = obtener_materia_prima_por_id(ingrediente["materia_prima_id"])
                    if not mp:
                        continue
                    cantidad = ingrediente["cantidad_necesaria"]
                    if rendimiento and rendimiento > 0:
                        cantidad = cantidad / rendimiento
                    total += cantidad * mp.costo_unitario * item.cantidad
    return total


def estado_resultado(inicio, fin):
    ventas = total_vendido_periodo(inicio, fin)
    costos = _costo_produccion_periodo(inicio, fin)
    gastos_ad = total_gastos_periodo(inicio, fin)
    resultado = ventas - costos - gastos_ad
    return {
        "ventas": ventas,
        "costos_produccion": costos,
        "gastos_adicionales": gastos_ad,
        "resultado_neto": resultado,
    }
