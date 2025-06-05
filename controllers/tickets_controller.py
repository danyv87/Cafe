import os
import json
import datetime
from collections import defaultdict
from models.ticket import Ticket
from models.venta_detalle import VentaDetalle
from controllers.recetas_controller import obtener_receta_por_producto_id
from controllers.materia_prima_controller import (
    obtener_materia_prima_por_id,
    listar_materias_primas,
    guardar_materias_primas,
)

# Determinar la ruta base de la aplicación.
if getattr(os.sys, 'frozen', False) and hasattr(os.sys, '_MEIPASS'):
    BASE_PATH = os.sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_PATH, "data", "tickets.json")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def cargar_tickets():
    """
    Carga la lista de tickets desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Ticket.from_dict(t) for t in data]
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía.")
        return []


def guardar_tickets(tickets):
    """
    Guarda la lista de objetos Ticket en el archivo JSON.
    """
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tickets], f, indent=4)


def registrar_ticket(cliente, items_venta_detalle):
    """
    Registra un nuevo ticket de venta con múltiples ítems y deduce el stock de materias primas.
    Args:
        cliente (str): Nombre del cliente.
        items_venta_detalle (list): Lista de objetos VentaDetalle.
    Raises:
        ValueError: Si el cliente está vacío, no hay ítems en el ticket,
                    o si el stock de alguna materia prima es insuficiente.
    Returns:
        Ticket: El objeto Ticket recién registrado.
    """
    if not cliente or len(cliente.strip()) == 0:
        raise ValueError("El nombre del cliente no puede estar vacío.")
    if not items_venta_detalle:
        raise ValueError("El ticket debe contener al menos un producto.")

    # --- Verificación de stock antes de registrar el ticket ---
    # Trabajamos sobre una copia de las materias primas para modificar el stock correctamente
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
                if materia_prima.stock < cantidad_a_deducir:
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

    # Crear y guardar el ticket
    tickets = cargar_tickets()
    nuevo_ticket = Ticket(cliente=cliente, items_venta=items_venta_detalle)
    tickets.append(nuevo_ticket)
    guardar_tickets(tickets)
    return nuevo_ticket


def listar_tickets():
    """
    Devuelve una lista de todos los tickets registrados.
    """
    return cargar_tickets()


def total_vendido_tickets():
    """
    Devuelve el total vendido sumando todos los tickets.
    """
    tickets = cargar_tickets()
    return sum(t.total for t in tickets)


def obtener_ventas_por_mes():
    """
    Retorna un diccionario {("YYYY-MM"): total_vendido_en_ese_mes}
    """
    tickets = cargar_tickets()
    ventas_por_mes = defaultdict(float)
    for t in tickets:
        # Suponemos que t.fecha es un string tipo '2024-06-05 09:41:25'
        # O bien un datetime, adaptamos ambos casos
        if hasattr(t, 'fecha') and t.fecha:
            if isinstance(t.fecha, str):
                fecha = datetime.datetime.strptime(t.fecha[:19], "%Y-%m-%d %H:%M:%S")
            else:
                fecha = t.fecha
            key = fecha.strftime("%Y-%m")
            ventas_por_mes[key] += t.total
    return dict(ventas_por_mes)


def obtener_ventas_por_semana():
    """
    Retorna un diccionario {("YYYY-WW"): total_vendido_en_esa_semana}
    """
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