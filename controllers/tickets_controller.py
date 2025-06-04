import json
import os
import sys  # Importar el módulo sys para PyInstaller
from datetime import datetime
from collections import defaultdict
from models.ticket import Ticket
from models.venta_detalle import VentaDetalle
from controllers.productos_controller import listar_productos
from controllers.recetas_controller import obtener_receta_por_producto_id  # ¡Nueva importación!
from controllers.materia_prima_controller import actualizar_stock_materia_prima, \
    obtener_materia_prima_por_id  # ¡Nuevas importaciones!

# Determinar la ruta base de la aplicación.
# sys._MEIPASS es una variable especial que PyInstaller establece
# y apunta a la carpeta temporal donde se extraen los archivos empaquetados.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Estamos en un ejecutable PyInstaller
    BASE_PATH = sys._MEIPASS
else:
    # Estamos en un entorno de desarrollo normal
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta completa al archivo JSON
DATA_PATH = os.path.join(BASE_PATH, "data", "tickets.json")

# Asegurarse de que la carpeta 'data' exista
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
    # Esto es crucial para evitar registrar una venta y luego fallar en la deducción.
    for item in items_venta_detalle:
        receta = obtener_receta_por_producto_id(item.producto_id)
        if receta and receta.ingredientes:
            for ingrediente in receta.ingredientes:
                mp_id = ingrediente["materia_prima_id"]
                cantidad_necesaria_por_unidad = ingrediente["cantidad_necesaria"]

                materia_prima = obtener_materia_prima_por_id(mp_id)
                if not materia_prima:
                    raise ValueError(f"Materia prima '{ingrediente.get('nombre_materia_prima',mp_id)}' no encontrada para la receta del producto '{item.nombre_producto}'.")

                cantidad_a_deducir = item.cantidad * cantidad_necesaria_por_unidad
                if materia_prima.stock < cantidad_a_deducir:
                    raise ValueError(
                        f"Stock insuficiente de '{materia_prima.nombre}' para producir '{item.nombre_producto}'. Se necesitan {cantidad_a_deducir} {materia_prima.unidad_medida} pero solo hay {materia_prima.stock} {materia_prima.unidad_medida}.")

    # Si todas las verificaciones de stock pasaron, procedemos a registrar el ticket y deducir el stock
    tickets = cargar_tickets()
    nuevo_ticket = Ticket(
        cliente=cliente.strip(),
        items_venta=items_venta_detalle
    )
    tickets.append(nuevo_ticket)
    guardar_tickets(tickets)

    # --- Deducción de stock después de registrar el ticket ---
    for item in items_venta_detalle:
        receta = obtener_receta_por_producto_id(item.producto_id)
        if receta and receta.ingredientes:
            for ingrediente in receta.ingredientes:
                mp_id = ingrediente["materia_prima_id"]
                cantidad_necesaria_por_unidad = ingrediente["cantidad_necesaria"]
                cantidad_a_deducir = item.cantidad * cantidad_necesaria_por_unidad

                # Llamar a la función de actualización de stock para deducir
                actualizar_stock_materia_prima(mp_id, -cantidad_a_deducir)  # Usar negativo para restar

    return nuevo_ticket


def listar_tickets():
    """
    Retorna la lista completa de tickets.
    """
    return cargar_tickets()


def total_vendido_tickets():
    """
    Calcula y retorna el total de todas las ventas registradas en todos los tickets.
    """
    tickets = cargar_tickets()
    return round(sum(t.total for t in tickets), 2)


def obtener_ventas_por_mes():
    """
    Calcula el total de ventas agrupadas por mes y año.
    Retorna una lista de tuplas (mes_año, total_vendido_ese_mes) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-01', 'Gs 150.000,00'), ('2023-02', 'Gs 200.000,00')]
    """
    tickets = cargar_tickets()
    ventas_mensuales = defaultdict(float)  # Usamos defaultdict para sumar fácilmente los totales por mes

    for ticket in tickets:
        try:
            # Parseamos la fecha del ticket para obtener el mes y año
            fecha_dt = datetime.strptime(ticket.fecha, "%Y-%m-%d %H:%M:%S")
            mes_año = fecha_dt.strftime("%Y-%m")  # Formato "YYYY-MM"
            ventas_mensuales[mes_año] += ticket.total
        except ValueError:
            # Si la fecha del ticket no tiene el formato esperado, la ignoramos o manejamos el error
            print(
                f"Advertencia: Fecha de ticket inválida '{ticket.fecha}'. Se ignorará este ticket para estadísticas mensuales.")
            continue
        except Exception as e:
            print(f"Error inesperado al procesar fecha del ticket '{ticket.fecha}': {e}")
            continue

    # Convertimos el defaultdict a una lista de tuplas y la ordenamos cronológicamente
    ventas_ordenadas = sorted(ventas_mensuales.items())

    # Formatear los totales con separador de miles (punto) y decimales (coma), y signo de moneda "Gs "
    formatted_ventas = []
    for mes_año, total in ventas_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_ventas.append((mes_año, f"Gs {total_str}"))

    return formatted_ventas


def obtener_ventas_por_semana():
    """
    Calcula el total de ventas agrupadas por semana y año.
    La semana se representa como 'YYYY-WNN' (Año-Número de Semana).
    Retorna una lista de tuplas (semana_año, total_vendido_esa_semana) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-W01', 'Gs 75.000,00'), ('2023-W02', 'Gs 100.000,00')]
    """
    tickets = cargar_tickets()
    ventas_semanales = defaultdict(float)

    for ticket in tickets:
        try:
            fecha_dt = datetime.strptime(ticket.fecha, "%Y-%m-%d %H:%M:%S")
            # %G: Año ISO, %V: Número de semana ISO (01-53), %u: Día de la semana ISO (1 para lunes)
            # Usamos %G-%V para obtener el formato Año-Semana
            semana_año = fecha_dt.strftime("%G-W%V")
            ventas_semanales[semana_año] += ticket.total
        except ValueError:
            print(
                f"Advertencia: Fecha de ticket inválida '{ticket.fecha}'. Se ignorará este ticket para estadísticas semanales.")
            continue
        except Exception as e:
            print(f"Error inesperado al procesar fecha del ticket '{ticket.fecha}': {e}")
            continue

    ventas_ordenadas = sorted(ventas_semanales.items())

    formatted_ventas = []
    for semana_año, total in ventas_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_ventas.append((semana_año, f"Gs {total_str}"))

    return formatted_ventas
