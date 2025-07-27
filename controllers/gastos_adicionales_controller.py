import os
import sys  # Importar el módulo sys para PyInstaller
import logging
from utils.json_utils import read_json, write_json
from collections import defaultdict
from datetime import datetime

# Importa tus modelos según corresponda, por ejemplo:
from models.gasto_adicional import GastoAdicional

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

DATA_PATH = os.path.join(BASE_PATH, "data", "gastos_adicionales.json")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def cargar_gastos_adicionales():
    """
    Carga la lista de gastos adicionales desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    data = read_json(DATA_PATH)
    return [GastoAdicional.from_dict(ga) for ga in data]

def guardar_gastos_adicionales(gastos_adicionales):
    """
    Guarda la lista de objetos GastoAdicional en el archivo JSON.
    """
    write_json(DATA_PATH, [ga.to_dict() for ga in gastos_adicionales])

def validar_gasto_adicional(nombre, monto):
    """
    Valida los datos de un gasto adicional.
    Retorna True si es válido, False y un mensaje de error en caso contrario.
    """
    if not nombre or not isinstance(nombre, str) or len(nombre.strip()) == 0:
        return False, "El nombre del gasto no puede estar vacío."
    if not isinstance(monto, (int, float)) or monto <= 0:
        return False, "El monto del gasto debe ser un número positivo."
    return True, ""

def agregar_gasto_adicional(nombre, monto, fecha=None, descripcion=None):
    """
    Agrega un nuevo gasto adicional a la lista y lo guarda.
    """
    es_valido, mensaje_error = validar_gasto_adicional(nombre, monto)
    if not es_valido:
        raise ValueError(mensaje_error)

    gastos_adicionales = cargar_gastos_adicionales()
    nuevo_gasto = GastoAdicional(
        nombre.strip(),
        monto,
        fecha,
        descripcion.strip() if descripcion else ""
    )
    gastos_adicionales.append(nuevo_gasto)
    guardar_gastos_adicionales(gastos_adicionales)
    return nuevo_gasto

def listar_gastos_adicionales():
    """
    Retorna la lista completa de gastos adicionales.
    """
    return cargar_gastos_adicionales()

def eliminar_gasto_adicional(id_gasto):
    """
    Elimina un gasto adicional de la lista por su ID.
    """
    gastos_adicionales = cargar_gastos_adicionales()
    gastos_original_count = len(gastos_adicionales)
    gastos_adicionales = [ga for ga in gastos_adicionales if ga.id != id_gasto]

    if len(gastos_adicionales) == gastos_original_count:
        raise ValueError(f"Gasto adicional con ID '{id_gasto}' no encontrado para eliminación.")

    guardar_gastos_adicionales(gastos_adicionales)
    return True

def obtener_gastos_adicionales_por_mes():
    """
    Calcula el total de gastos adicionales agrupados por mes y año.
    Retorna una lista de tuplas (mes_año, total_gastado_ese_mes) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-01', 'Gs 150.000,00'), ('2023-02', 'Gs 200.000,00')]
    """
    gastos = cargar_gastos_adicionales()
    gastos_mensuales = defaultdict(float)

    for gasto in gastos:
        try:
            fecha_dt = datetime.strptime(gasto.fecha, "%Y-%m-%d %H:%M:%S")
            mes_año = fecha_dt.strftime("%Y-%m")
            gastos_mensuales[mes_año] += gasto.monto
        except ValueError:
            logger.error(
                f"Advertencia: Fecha de gasto inválida '{gasto.fecha}'. Se ignorará este gasto para estadísticas mensuales."
            )
            continue
        except Exception as e:
            logger.error(
                f"Error inesperado al procesar fecha del gasto '{gasto.fecha}': {e}"
            )
            continue

    gastos_ordenados = sorted(gastos_mensuales.items())

    formatted_gastos = []
    for mes_año, total in gastos_ordenados:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_gastos.append((mes_año, f"Gs {total_str}"))

    return formatted_gastos

def obtener_gastos_adicionales_por_semana():
    """
    Calcula el total de gastos adicionales agrupados por semana y año.
    La semana se representa como 'YYYY-WNN' (Año-Número de Semana).
    Retorna una lista de tuplas (semana_año, total_gastado_esa_semana) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-W01', 'Gs 25.000,00'), ('2023-W02', 'Gs 30.000,00')]
    """
    gastos = cargar_gastos_adicionales()
    gastos_semanales = defaultdict(float)

    for gasto in gastos:
        try:
            fecha_dt = datetime.strptime(gasto.fecha, "%Y-%m-%d %H:%M:%S")
            semana_año = fecha_dt.strftime("%G-W%V") # Formato Año-Semana ISO
            gastos_semanales[semana_año] += gasto.monto
        except ValueError:
            logger.error(
                f"Advertencia: Fecha de gasto inválida '{gasto.fecha}'. Se ignorará este gasto para estadísticas semanales."
            )
            continue
        except Exception as e:
            logger.error(
                f"Error inesperado al procesar fecha del gasto '{gasto.fecha}': {e}"
            )
            continue

    gastos_ordenados = sorted(gastos_semanales.items())

    formatted_gastos = []
    for semana_año, total in gastos_ordenados:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_gastos.append((semana_año, f"Gs {total_str}"))

    return formatted_gastos

def obtener_gastos_adicionales_por_dia():
    """
    Calcula el total de gastos adicionales agrupados por día.
    Retorna una lista de tuplas (YYYY-MM-DD, total_gastos_dia) ordenada,
    con el total formateado como string de moneda.
    """
    gastos = cargar_gastos_adicionales()
    gastos_dia = defaultdict(float)
    for gasto in gastos:
        try:
            fecha_dt = datetime.strptime(gasto.fecha, "%Y-%m-%d %H:%M:%S")
            dia = fecha_dt.strftime("%Y-%m-%d")
            gastos_dia[dia] += gasto.monto
        except Exception as e:
            logger.error(f"Error procesando fecha de gasto adicional: {e}")
            continue
    gastos_ordenados = sorted(gastos_dia.items())
    formatted = []
    for dia, total in gastos_ordenados:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted.append((dia, f"Gs {total_str}"))
    return formatted