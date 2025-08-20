import logging
from typing import List

from utils.json_utils import read_json, write_json
from utils.history_utils import listar_versiones
from models.compra import Compra
from models.compra_detalle import CompraDetalle
from utils import receipt_parser
from controllers.materia_prima_controller import (
    agregar_materia_prima,
    actualizar_stock_materia_prima,
)
import config
from collections import defaultdict
from datetime import datetime  # <-- ¡Necesario para funciones de fecha!

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


def _solicitar_datos_materia_prima(nombre):
    """Pide al usuario datos para crear una nueva materia prima o la omite.

    Retorna ``None`` si el usuario decide omitir la materia prima. Intenta usar
    diálogos de ``tkinter`` y cae a la entrada estándar si el entorno gráfico no
    está disponible.
    """

    try:  # pragma: no cover - prefer GUI but fall back to CLI in tests
        import tkinter as tk
        from tkinter import simpledialog

        root = tk.Tk()
        root.withdraw()
        accion = simpledialog.askstring(
            "Materia prima faltante",
            f"¿Desea crear u omitir '{nombre}'?",
            parent=root,
        )
        if accion is None or accion.strip().lower() != "crear":
            root.destroy()
            return None
        unidad = simpledialog.askstring(
            "Materia prima faltante",
            f"Unidad de medida para '{nombre}':",
            parent=root,
        )
        if unidad is None:
            raise ValueError("Operación cancelada por el usuario.")
        costo = simpledialog.askfloat(
            "Materia prima faltante",
            f"Costo unitario para '{nombre}':",
            parent=root,
        )
        if costo is None:
            raise ValueError("Operación cancelada por el usuario.")
        stock = simpledialog.askfloat(
            "Materia prima faltante",
            f"Stock inicial para '{nombre}':",
            parent=root,
        )
        if stock is None:
            raise ValueError("Operación cancelada por el usuario.")
        root.destroy()
        return unidad, float(costo), float(stock)
    except Exception:
        accion = (
            input(
                f"Materia prima '{nombre}' no encontrada. ¿Crear u omitir? (crear/omitir): "
            )
            .strip()
            .lower()
        )
        if accion != "crear":
            return None
        unidad = input(f"Ingrese la unidad de medida para '{nombre}': ").strip()
        costo = float(input(f"Ingrese el costo unitario para '{nombre}': "))
        stock = float(input(f"Ingrese el stock inicial para '{nombre}': "))
        return unidad, costo, stock


def registrar_compra_desde_imagen(proveedor, path_imagen, como_compra=False):
    """Procesa un comprobante en ``path_imagen`` y retorna los ítems obtenidos.

    La información recuperada **no** se persiste ni actualiza el stock hasta
    que los ítems sean confirmados y registrados mediante
    :func:`registrar_compra`.

    Args:
        proveedor (str): Nombre del proveedor.
        path_imagen (str): Ruta del archivo de imagen del comprobante.
        como_compra (bool): Si es ``True`` se devuelve un objeto :class:`Compra`;
            en caso contrario, se retorna la lista de diccionarios de ítems.

    Returns:
        list[dict] | Compra: Ítems validados del comprobante o una ``Compra``
            temporal si ``como_compra`` es ``True``.

    Raises:
        ValueError: Se propaga con alguno de los siguientes mensajes para
            facilitar el diagnóstico del problema:

            - ``"El nombre del proveedor no puede estar vacío."``
            - ``"No se pudo procesar la imagen por un problema de conexión."``
            - ``"No hay backend disponible para procesar imágenes de recibo."``
            - Mensajes emitidos por :func:`parse_receipt_image` (por ejemplo,
              ``"Cantidad o precio inválidos en el comprobante"``).
            - ``"No se pudo interpretar la imagen del comprobante."`` cuando
              ocurre un error inesperado.
            - Mensajes de validación como ``"producto_id inválido en la
              imagen"`` o ``"cantidad debe ser un número positivo."``.
    """

    if not proveedor or len(proveedor.strip()) == 0:
        raise ValueError("El nombre del proveedor no puede estar vacío.")

    omitidos: List[str] = []
    while True:
        try:
            items_dict, faltantes = receipt_parser.parse_receipt_image(
                path_imagen, omitidos=omitidos
            )
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Error de red al procesar '{path_imagen}': {e}")
            raise ValueError(
                "No se pudo procesar la imagen por un problema de conexión."
            ) from e
        except NotImplementedError as e:
            logger.error(
                f"Funcionalidad no disponible al procesar '{path_imagen}': {e}"
            )
            raise ValueError(str(e)) from e
        except FileNotFoundError as e:
            logger.error(f"Comprobante no accesible '{path_imagen}': {e}")
            raise ValueError(
                "El comprobante no existe o no es accesible."
            ) from e
        except ValueError as e:
            logger.error(f"Error al interpretar la imagen '{path_imagen}': {e}")
            raise ValueError(str(e)) from e
        except Exception as e:
            logger.error(f"Error al interpretar la imagen '{path_imagen}': {e}")
            raise ValueError(
                "No se pudo interpretar la imagen del comprobante."
            ) from e

        if faltantes:
            registrados: List[str] = []
            for raw in faltantes:
                nombre_mp = raw.get("nombre_producto") or raw.get("producto") or ""
                datos = _solicitar_datos_materia_prima(nombre_mp)
                if datos is None:
                    omitidos.append(nombre_mp)
                    continue
                unidad, costo, stock = datos
                agregar_materia_prima(nombre_mp, unidad, costo, stock)
                registrados.append(nombre_mp)
            if registrados:
                receipt_parser.clear_cache()
                continue
        break

    if not isinstance(items_dict, list):
        raise ValueError("Formato de datos inválido del comprobante.")

    items_validados = []
    for item in items_dict:
        try:
            producto_id = int(item["producto_id"])
            nombre = item["nombre_producto"].strip()
            cantidad = float(item["cantidad"])
            costo_unitario = float(item["costo_unitario"])
            descripcion = item.get("descripcion_adicional", "")
        except Exception as e:  # pragma: no cover - fallthrough validation
            logger.error(f"Error al convertir datos del comprobante: {e}")
            raise ValueError("Datos de compra inválidos en la imagen.") from e

        if not producto_id:
            raise ValueError("producto_id inválido en la imagen.")
        if not isinstance(nombre, str) or not nombre:
            raise ValueError("nombre_producto inválido en la imagen.")
        if cantidad <= 0:
            raise ValueError("cantidad debe ser un número positivo.")
        if costo_unitario <= 0:
            raise ValueError("costo_unitario debe ser un número positivo.")
        if not isinstance(descripcion, str):
            raise ValueError("descripcion_adicional debe ser texto.")

        items_validados.append(
            {
                "producto_id": producto_id,
                "nombre_producto": nombre,
                "cantidad": cantidad,
                "costo_unitario": costo_unitario,
                "descripcion_adicional": descripcion,
            }
        )

    if como_compra:
        detalles = [
            CompraDetalle(
                producto_id=item["producto_id"],
                nombre_producto=item["nombre_producto"],
                cantidad=item["cantidad"],
                costo_unitario=item["costo_unitario"],
                descripcion_adicional=item.get("descripcion_adicional", ""),
            )
            for item in items_validados
        ]
        return Compra(proveedor=proveedor.strip(), items_compra=detalles)

    return items_validados


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
