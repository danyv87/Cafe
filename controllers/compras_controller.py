import logging
from utils.json_utils import read_json, write_json
from utils.history_utils import listar_versiones
from models.compra import Compra
from models.compra_detalle import CompraDetalle
from utils.receipt_parser import parse_receipt_image
import config
from collections import defaultdict
from datetime import datetime  # <-- ¡Necesario para funciones de fecha!
from controllers.materia_prima_controller import actualizar_stock_materia_prima

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ruta por defecto donde se almacenarán las compras
DATA_PATH = config.get_data_path("compras.json")


def cargar_compras():
    """
    Carga la lista de compras desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    logger.debug(f"Intentando cargar compras desde: {DATA_PATH}")
    data = read_json(DATA_PATH)
    logger.debug(f"Compras cargadas (raw data): {data}")
    return [Compra.from_dict(c) for c in data]


def guardar_compras(compras):
    """
    Guarda la lista de objetos Compra en el archivo JSON.
    """
    logger.debug(f"Intentando guardar {len(compras)} compras en: {DATA_PATH}")
    write_json(DATA_PATH, [c.to_dict() for c in compras])
    logger.debug("Compras guardadas con éxito.")
    exportar_compras_excel(compras)


def exportar_compras_excel(compras):
    """Exporta la lista de compras a ``compras.xlsx``.

    Si ``pandas``/``openpyxl`` no están instalados o ocurre algún otro error
    durante la exportación, se registra una advertencia y la aplicación sigue
    funcionando con normalidad.
    """

    try:  # pragma: no cover - la exportación es best effort
        import pandas as pd

        df = pd.DataFrame([c.to_dict() for c in compras])
        excel_path = config.get_data_path("compras.xlsx")
        df.to_excel(excel_path, index=False)
    except ImportError as e:
        logger.warning(
            f"No se pudo exportar las compras a Excel por falta de dependencias: {e}"
        )
    except Exception as e:
        logger.warning(f"No se pudo exportar las compras a Excel: {e}")


def registrar_compra_desde_imagen(proveedor, path_imagen):
    """Procesa un comprobante en *path_imagen* y construye una ``Compra``.

    La compra resultante **no** se persiste ni actualiza el stock hasta que
    los ítems sean confirmados. Para guardar definitivamente la compra debe
    llamarse a :func:`registrar_compra` con los datos retornados.

    Args:
        proveedor (str): Nombre del proveedor.
        path_imagen (str): Ruta del archivo de imagen del comprobante.

    Returns:
        Compra: Compra con los ítems obtenidos desde la imagen.

    Raises:
        ValueError: Si ocurre un problema de conexión o si los datos del
            comprobante no pueden interpretarse.
    """

    if not proveedor or len(proveedor.strip()) == 0:
        raise ValueError("El nombre del proveedor no puede estar vacío.")

    try:
        items_dict = parse_receipt_image(path_imagen)
    except (ConnectionError, TimeoutError) as e:
        logger.error(f"Error de red al procesar '{path_imagen}': {e}")
        raise ValueError(
            "No se pudo procesar la imagen por un problema de conexión."
        ) from e
    except Exception as e:
        logger.error(f"Error al interpretar la imagen '{path_imagen}': {e}")
        raise ValueError(
            "No se pudo interpretar la imagen del comprobante."
        ) from e

    if not isinstance(items_dict, list):
        raise ValueError("Formato de datos inválido del comprobante.")

    try:
        detalles = [
            CompraDetalle(
                producto_id=item.get("producto_id"),
                nombre_producto=item.get("nombre_producto"),
                cantidad=item.get("cantidad"),
                costo_unitario=item.get("costo_unitario"),
                descripcion_adicional=item.get("descripcion_adicional", ""),
            )
            for item in items_dict
        ]
    except Exception as e:
        logger.error(f"Error al convertir datos del comprobante: {e}")
        raise ValueError("Datos de compra inválidos en la imagen.") from e

    return Compra(proveedor=proveedor.strip(), items_compra=detalles)


def registrar_compra(proveedor, items_compra_detalle, fecha=None):
    """
    Registra una nueva compra con múltiples ítems y actualiza el stock de materias primas.
    Args:
        proveedor (str): Nombre del proveedor.
        items_compra_detalle (list): Lista de objetos CompraDetalle (ahora representando materias primas).
        fecha (str, optional): Fecha y hora de la compra en formato "YYYY-MM-DD HH:MM:SS". Si no se
            proporciona, se utilizará la fecha y hora actuales.
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
        items_compra=items_compra_detalle,
        fecha=fecha
    )
    compras.append(nueva_compra)
    guardar_compras(compras)

    # ¡Actualizar el stock de materias primas!
    for item in items_compra_detalle:
        try:
            # El producto_id en CompraDetalle ahora es el ID de la MateriaPrima
            actualizar_stock_materia_prima(item.producto_id, item.cantidad)
        except ValueError as e:
            logger.error(
                f"Error al actualizar stock de materia prima '{item.nombre_producto}': {e}"
            )
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
            logger.error(
                f"Advertencia: Fecha de compra inválida '{compra.fecha}'. Se ignorará esta compra para estadísticas mensuales."
            )
            continue
        except Exception as e:
            logger.error(
                f"Error inesperado al procesar fecha de compra '{compra.fecha}': {e}"
            )
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
            logger.error(
                f"Advertencia: Fecha de compra inválida '{compra.fecha}'. Se ignorará esta compra para estadísticas semanales."
            )
            continue
        except Exception as e:
            logger.error(
                f"Error inesperado al procesar fecha de compra '{compra.fecha}': {e}"
            )
            continue

    compras_ordenadas = sorted(compras_semanales.items())

    formatted_compras = []
    for semana_año, total in compras_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_compras.append((semana_año, f"Gs {total_str}"))

    return formatted_compras

def obtener_compras_por_dia():
    """
    Calcula el total de compras agrupadas por día.
    Retorna una lista de tuplas (YYYY-MM-DD, total_compras_dia) ordenada,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2025-06-15', 'Gs 120.000'), ...]
    """
    compras = cargar_compras()
    compras_dia = defaultdict(float)
    for compra in compras:
        try:
            fecha_dt = datetime.strptime(compra.fecha, "%Y-%m-%d %H:%M:%S")
            dia = fecha_dt.strftime("%Y-%m-%d")
            compras_dia[dia] += compra.total
        except Exception as e:
            logger.error(f"Error procesando fecha de compra: {e}")
            continue
    compras_ordenadas = sorted(compras_dia.items())
    formatted = []
    for dia, total in compras_ordenadas:
        total_str = f"{total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted.append((dia, f"Gs {total_str}"))
    return formatted


def listar_versiones_compras():
    """Lista las versiones disponibles del archivo de compras."""
    return listar_versiones(DATA_PATH)


def restaurar_version_compras(ruta_version):
    """Restaura las compras desde la *ruta_version* indicada."""
    data = read_json(ruta_version)
    write_json(DATA_PATH, data)
    return [Compra.from_dict(c) for c in data]
