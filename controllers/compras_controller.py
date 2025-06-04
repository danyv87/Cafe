import json
import os
from datetime import datetime
from collections import defaultdict # Importa defaultdict para facilitar la suma
from models.compra import Compra # Importa el modelo Compra
from models.compra_detalle import CompraDetalle # Importa el modelo CompraDetalle
from controllers.productos_controller import listar_productos, obtener_producto_por_id, guardar_productos # Necesitamos esto para actualizar stock

DATA_PATH = "data/compras.json" # La ruta de datos ahora apunta a compras.json


def cargar_compras():
    """
    Carga la lista de compras desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Convierte los diccionarios cargados en objetos Compra
            return [Compra.from_dict(c) for c in data]
    except json.JSONDecodeError:
        # Maneja el caso de un archivo JSON vacío o malformado
        print(f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía.")
        return []


def guardar_compras(compras):
    """
    Guarda la lista de objetos Compra en el archivo JSON.
    """
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        # Convierte los objetos Compra a diccionarios para guardarlos como JSON
        json.dump([c.to_dict() for c in compras], f, indent=4)


def registrar_compra(proveedor, items_compra_detalle):
    """
    Registra una nueva compra con múltiples ítems.
    Args:
        proveedor (str): Nombre del proveedor.
        items_compra_detalle (list): Lista de objetos CompraDetalle.
    Raises:
        ValueError: Si el proveedor está vacío o no hay ítems en la compra.
    Returns:
        Compra: El objeto Compra recién registrado.
    """
    if not proveedor or len(proveedor.strip()) == 0:
        raise ValueError("El nombre del proveedor no puede estar vacío.")
    if not items_compra_detalle:
        raise ValueError("La compra debe contener al menos un producto.")

    compras = cargar_compras()
    nueva_compra = Compra(
        proveedor=proveedor.strip(), # Elimina espacios en blanco del nombre del proveedor
        items_compra=items_compra_detalle # La lista de CompraDetalle
    )
    compras.append(nueva_compra)
    guardar_compras(compras)

    # Opcional: Aquí podrías integrar la actualización del stock de productos
    # Por ahora, solo registramos la compra. Si en el futuro se implementa
    # la gestión de inventario, este es el lugar para incrementar el stock.
    # for item in items_compra_detalle:
    #     producto = obtener_producto_por_id(item.producto_id)
    #     if producto:
    #         producto.stock += item.cantidad
    #         # Necesitarías una función en productos_controller para guardar un solo producto
    #         # o cargar todos y luego guardar_productos(productos)

    return nueva_compra


def listar_compras():
    """
    Retorna la lista completa de compras.
    """
    return cargar_compras()


def total_comprado():
    """
    Calcula y retorna el total de todas las compras registradas.
    """
    compras = cargar_compras()
    return round(sum(c.total for c in compras), 2)

def obtener_compras_por_mes():
    """
    Calcula el total de compras agrupadas por mes y año.
    Retorna una lista de tuplas (mes_año, total_comprado_ese_mes) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-01', 'Gs 50.000,00'), ('2023-02', 'Gs 75.000,00')]
    """
    compras = cargar_compras()
    compras_mensuales = defaultdict(float)

    for compra in compras:
        try:
            fecha_dt = datetime.strptime(compra.fecha, "%Y-%m-%d %H:%M:%S")
            mes_año = fecha_dt.strftime("%Y-%m")
            compras_mensuales[mes_año] += compra.total
        except ValueError:
            print(f"Advertencia: Fecha de compra inválida '{compra.fecha}'. Se ignorará esta compra para estadísticas mensuales.")
            continue
        except Exception as e:
            print(f"Error inesperado al procesar fecha de compra '{compra.fecha}': {e}")
            continue

    compras_ordenadas = sorted(compras_mensuales.items())

    formatted_compras = []
    for mes_año, total in compras_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_compras.append((mes_año, f"Gs {total_str}"))

    return formatted_compras

def obtener_compras_por_semana():
    """
    Calcula el total de compras agrupadas por semana y año.
    La semana se representa como 'YYYY-WNN' (Año-Número de Semana).
    Retorna una lista de tuplas (semana_año, total_comprado_esa_semana) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-W01', 'Gs 25.000,00'), ('2023-W02', 'Gs 30.000,00')]
    """
    compras = cargar_compras()
    compras_semanales = defaultdict(float)

    for compra in compras:
        try:
            fecha_dt = datetime.strptime(compra.fecha, "%Y-%m-%d %H:%M:%S")
            semana_año = fecha_dt.strftime("%G-W%V") # Formato Año-Semana ISO
            compras_semanales[semana_año] += compra.total
        except ValueError:
            print(f"Advertencia: Fecha de compra inválida '{compra.fecha}'. Se ignorará esta compra para estadísticas semanales.")
            continue
        except Exception as e:
            print(f"Error inesperado al procesar fecha de compra '{compra.fecha}': {e}")
            continue

    compras_ordenadas = sorted(compras_semanales.items())

    formatted_compras = []
    for semana_año, total in compras_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_compras.append((semana_año, f"Gs {total_str}"))

    return formatted_compras
