import json
import os
import sys # Importar el módulo sys para PyInstaller
from datetime import datetime
from collections import defaultdict
from models.compra import Compra
from models.compra_detalle import CompraDetalle
from controllers.materia_prima_controller import actualizar_stock_materia_prima

# Determinar la ruta base de la aplicación para compatibilidad con PyInstaller.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_PATH = sys._MEIPASS
else:
    # En ambiente de desarrollo, queremos el directorio raíz del proyecto
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

DATA_PATH = os.path.join(BASE_PATH, "data", "compras.json")

# Asegurarse de que la carpeta 'data' exista
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def cargar_compras():
    """
    Carga la lista de compras desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    print(f"DEBUG: Intentando cargar compras desde: {DATA_PATH}") # DEBUG LINE
    if not os.path.exists(DATA_PATH):
        print(f"DEBUG: Archivo de compras no encontrado: {DATA_PATH}") # DEBUG LINE
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"DEBUG: Compras cargadas (raw data): {data}") # DEBUG LINE
            return [Compra.from_dict(c) for c in data]
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía.")
        return []
    except Exception as e:
        print(f"DEBUG: Error inesperado al cargar compras: {e}") # DEBUG LINE
        return []


def guardar_compras(compras):
    """
    Guarda la lista de objetos Compra en el archivo JSON.
    """
    print(f"DEBUG: Intentando guardar {len(compras)} compras en: {DATA_PATH}") # DEBUG LINE
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in compras], f, indent=4)
    print("DEBUG: Compras guardadas con éxito.") # DEBUG LINE


def registrar_compra(proveedor, items_compra_detalle):
    """
    Registra una nueva compra con múltiples ítems y actualiza el stock de materias primas.
    Args:
        proveedor (str): Nombre del proveedor.
        items_compra_detalle (list): Lista de objetos CompraDetalle (ahora representando materias primas).
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
        proveedor=proveedor.strip(),
        items_compra=items_compra_detalle
    )
    compras.append(nueva_compra)
    guardar_compras(compras)

    # ¡Actualizar el stock de materias primas!
    for item in items_compra_detalle:
        try:
            # El producto_id en CompraDetalle ahora es el ID de la MateriaPrima
            actualizar_stock_materia_prima(item.producto_id, item.cantidad)
        except ValueError as e:
            print(f"Error al actualizar stock de materia prima '{item.nombre_producto}': {e}")
            raise ValueError(f"Error al actualizar stock de '{item.nombre_producto}': {e}")

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
