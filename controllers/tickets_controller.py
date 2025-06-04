import json
import os
from models.ticket import Ticket # Importa el nuevo modelo Ticket
from models.venta_detalle import VentaDetalle # Importa el modelo VentaDetalle
from controllers.productos_controller import listar_productos # Todavía necesitamos los productos

DATA_PATH = "data/tickets.json" # La ruta de datos ahora apunta a tickets.json


def cargar_tickets(): # Renombrada de cargar_ventas
    """
    Carga la lista de tickets desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Convierte los diccionarios cargados en objetos Ticket
            return [Ticket.from_dict(t) for t in data]
    except json.JSONDecodeError:
        # Maneja el caso de un archivo JSON vacío o malformado
        print(f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía.")
        return []


def guardar_tickets(tickets): # Renombrada de guardar_ventas
    """
    Guarda la lista de objetos Ticket en el archivo JSON.
    """
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        # Convierte los objetos Ticket a diccionarios para guardarlos como JSON
        json.dump([t.to_dict() for t in tickets], f, indent=4)


def registrar_ticket(cliente, items_venta_detalle): # Nueva función para registrar un ticket completo
    """
    Registra un nuevo ticket de venta con múltiples ítems.
    Args:
        cliente (str): Nombre del cliente.
        items_venta_detalle (list): Lista de objetos VentaDetalle.
    Raises:
        ValueError: Si el cliente está vacío o no hay ítems en el ticket.
    Returns:
        Ticket: El objeto Ticket recién registrado.
    """
    if not cliente or len(cliente.strip()) == 0:
        raise ValueError("El nombre del cliente no puede estar vacío.")
    if not items_venta_detalle:
        raise ValueError("El ticket debe contener al menos un producto.")

    tickets = cargar_tickets()
    nuevo_ticket = Ticket(
        cliente=cliente.strip(), # Elimina espacios en blanco del nombre del cliente
        items_venta=items_venta_detalle # La lista de VentaDetalle
    )
    tickets.append(nuevo_ticket)
    guardar_tickets(tickets)
    return nuevo_ticket


def listar_tickets(): # Renombrada de listar_ventas
    """
    Retorna la lista completa de tickets.
    """
    return cargar_tickets()


def total_vendido_tickets(): # Renombrada de total_vendido
    """
    Calcula y retorna el total de todas las ventas registradas en todos los tickets.
    """
    tickets = cargar_tickets()
    return round(sum(t.total for t in tickets), 2)

