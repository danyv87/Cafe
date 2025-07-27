import json
import os
import logging
from models.ticket import Ticket  # Ajusta según tus imports reales
import config
from collections import defaultdict
from controllers.materia_prima_controller import listar_materias_primas, guardar_materias_primas
from controllers.recetas_controller import obtener_receta_por_producto_id
import datetime

DATA_PATH = config.get_data_path("tickets.json")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def eliminar_ticket(ticket_id):
    tickets = cargar_tickets()
    tickets_filtrados = [t for t in tickets if t.id != ticket_id]
    if len(tickets_filtrados) == len(tickets):
        raise ValueError(f"No se encontró el ticket con ID {ticket_id}.")
    guardar_tickets(tickets_filtrados)
    return True

def cargar_tickets():
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Ticket.from_dict(t) for t in data]
    except json.JSONDecodeError:
        logger.error(
            f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía."
        )
        return []

def guardar_tickets(tickets):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tickets], f, indent=4)

def registrar_ticket(cliente, items_venta_detalle, forzar=False, fecha=None):
    """
    Registra un nuevo ticket de venta con múltiples ítems y deduce el stock de materias primas.
    Args:
        cliente (str): Nombre del cliente.
        items_venta_detalle (list): Lista de objetos VentaDetalle.
        forzar (bool): Si es True, permite stock negativo y solo advierte.
        fecha (str, opcional): Fecha y hora de la venta en formato 'YYYY-MM-DD HH:MM:SS'.
                               Si es None o vacío, se usará la fecha/hora actual.
    Raises:
        ValueError: Si el cliente está vacío, no hay ítems en el ticket,
                    o si el stock de alguna materia prima es insuficiente y no se fuerza.
    Returns:
        Ticket: El objeto Ticket recién registrado.
    """
    if not cliente or len(cliente.strip()) == 0:
        raise ValueError("El nombre del cliente no puede estar vacío.")
    if not items_venta_detalle:
        raise ValueError("El ticket debe contener al menos un producto.")

    # --- Verificación de stock antes de registrar el ticket ---
    materias_primas = listar_materias_primas()
    materias_prima_dict = {mp.id: mp for mp in materias_primas}

    for item in items_venta_detalle:
        receta = obtener_receta_por_producto_id(item.producto_id)
        if receta and receta.ingredientes:
            unidades_por_lote = getattr(receta, 'unidades_por_lote', None)
            for ingrediente in receta.ingredientes:
                mp_id = ingrediente["materia_prima_id"]
                cantidad_necesaria = ingrediente["cantidad_necesaria"]
                if unidades_por_lote and unidades_por_lote > 0:
                    cantidad_necesaria_por_unidad = cantidad_necesaria / unidades_por_lote
                else:
                    cantidad_necesaria_por_unidad = cantidad_necesaria
                materia_prima = materias_prima_dict.get(mp_id)
                if not materia_prima:
                    raise ValueError(
                        f"Materia prima '{ingrediente.get('nombre_materia_prima', mp_id)}' no encontrada para la receta del producto '{item.nombre_producto}'."
                    )
                cantidad_a_deducir = item.cantidad * cantidad_necesaria_por_unidad
                if materia_prima.stock < cantidad_a_deducir and not forzar:
                    raise ValueError(
                        f"Stock insuficiente de '{materia_prima.nombre}'. Se requieren {cantidad_a_deducir:.2f} {materia_prima.unidad_medida}, pero solo hay {materia_prima.stock:.2f}."
                    )

    # --- Descontar stock y registrar el ticket ---
    for item in items_venta_detalle:
        receta = obtener_receta_por_producto_id(item.producto_id)
        if receta and receta.ingredientes:
            unidades_por_lote = getattr(receta, 'unidades_por_lote', None)
            for ingrediente in receta.ingredientes:
                mp_id = ingrediente["materia_prima_id"]
                cantidad_necesaria = ingrediente["cantidad_necesaria"]
                if unidades_por_lote and unidades_por_lote > 0:
                    cantidad_necesaria_por_unidad = cantidad_necesaria / unidades_por_lote
                else:
                    cantidad_necesaria_por_unidad = cantidad_necesaria
                materia_prima = materias_prima_dict.get(mp_id)
                cantidad_a_deducir = item.cantidad * cantidad_necesaria_por_unidad
                materia_prima.stock -= cantidad_a_deducir

    guardar_materias_primas(list(materias_prima_dict.values()))

    # Si la fecha es None o vacía, usar la fecha/hora actual
    if not fecha or (isinstance(fecha, str) and fecha.strip() == ""):
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear y guardar el ticket
    tickets = cargar_tickets()
    nuevo_ticket = Ticket(cliente=cliente, items_venta=items_venta_detalle, fecha=fecha)
    tickets.append(nuevo_ticket)
    guardar_tickets(tickets)
    return nuevo_ticket

def listar_tickets():
    return cargar_tickets()

def total_vendido_tickets():
    tickets = cargar_tickets()
    return sum(t.total for t in tickets)

def obtener_ventas_por_mes():
    tickets = cargar_tickets()
    ventas_por_mes = defaultdict(float)
    for t in tickets:
        if hasattr(t, 'fecha') and t.fecha:
            if isinstance(t.fecha, str):
                fecha = datetime.datetime.strptime(t.fecha[:19], "%Y-%m-%d %H:%M:%S")
            else:
                fecha = t.fecha
            key = fecha.strftime("%Y-%m")
            ventas_por_mes[key] += t.total
    return dict(ventas_por_mes)

def obtener_ventas_por_semana():
    tickets = cargar_tickets()
    ventas_por_semana = defaultdict(float)
    for t in tickets:
        if hasattr(t, 'fecha') and t.fecha:
            if isinstance(t.fecha, str):
                fecha = datetime.datetime.strptime(t.fecha[:19], "%Y-%m-%d %H:%M:%S")
            else:
                fecha = t.fecha
            year, weeknum, _ = fecha.isocalendar()
            key = f"{year}-W{weeknum:02d}"
            ventas_por_semana[key] += t.total
    return dict(ventas_por_semana)

def obtener_ventas_por_dia():
    """
    Calcula el total de ventas agrupadas por día.
    Retorna una lista de tuplas (YYYY-MM-DD, total_ventas_dia) ordenada,
    con el total formateado como string de moneda.
    """
    tickets = cargar_tickets()
    ventas_dia = defaultdict(float)
    for t in tickets:
        if hasattr(t, 'fecha') and t.fecha:
            if isinstance(t.fecha, str):
                fecha = datetime.datetime.strptime(t.fecha[:19], "%Y-%m-%d %H:%M:%S")
            else:
                fecha = t.fecha
            dia = fecha.strftime("%Y-%m-%d")
            ventas_dia[dia] += t.total
    ventas_ordenadas = sorted(ventas_dia.items())
    formatted = []
    for dia, total in ventas_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted.append((dia, f"Gs {total_str}"))
    return formatted