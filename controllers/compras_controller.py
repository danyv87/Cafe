import logging
import sqlite3
from typing import List, Callable, Optional

from utils.json_utils import read_json, write_json
from models.compra import Compra
from models.compra_detalle import CompraDetalle
from models.proveedor import Proveedor
from utils import receipt_parser
from controllers.invoice_importer import InvoiceImporter
from controllers.materia_prima_controller import (
    agregar_materia_prima,
    actualizar_stock_materia_prima,
)
import config
from collections import defaultdict
from datetime import datetime  # <-- ¡Necesario para funciones de fecha!

# Configuración de logging estructurado


class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}
        return msg, kwargs


base_logger = logging.getLogger(__name__)
LOG_PATH = config.get_data_path("compras_import.log")
if not any(
    isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == LOG_PATH
    for h in base_logger.handlers
):
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(proveedor)s - %(archivo)s - %(message)s"
        )
    )
    base_logger.addHandler(file_handler)
logger = ContextAdapter(base_logger, {"proveedor": "-", "archivo": "-"})

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


def registrar_materias_primas_faltantes(
    faltantes: List[dict], datos_creacion: dict[str, tuple]
) -> tuple[dict[str, str], list[dict]]:
    """Registra materias primas faltantes a partir de datos ya validados.

    Args:
        faltantes: Lista de elementos detectados en el comprobante sin materia
            prima asociada.
        datos_creacion: Diccionario ``{nombre: (unidad, costo, stock)}`` con los
            datos para las materias primas que se desean crear.

    Returns:
        tuple[dict[str, str], list[dict]]: Una tupla con dos elementos:
            - Diccionario ``{nombre: id}`` de materias primas creadas.
            - Lista de diccionarios correspondientes a las materias primas que
              se decidieron omitir.
    """

    registrados: dict[str, str] = {}
    omitidos: list[dict] = []

    for raw in faltantes:
        nombre = raw.get("nombre_producto") or raw.get("producto") or ""
        if nombre in datos_creacion:
            unidad, costo, stock = datos_creacion[nombre]
            mp = agregar_materia_prima(nombre, unidad, costo, stock)
            registrados[nombre] = mp.id
        else:
            omitidos.append(raw)

    if registrados:
        receipt_parser.clear_cache()

    return registrados, omitidos


def registrar_compra_desde_imagen(
    proveedor: Proveedor,
    path_imagen,
    como_compra=False,
    output_dir=None,
    db_conn=None,
    omitidos=None,
    selector: Optional[Callable[[dict], bool]] = None,
    importer: Optional[InvoiceImporter] = None,
):
    """Procesa un comprobante en ``path_imagen`` y retorna los ítems obtenidos.

    Además de los ítems validados, también se obtienen aquellos que quedan
    pendientes por no tener una materia prima asociada. La información
    recuperada **no** se persiste ni actualiza el stock hasta que los ítems sean
    confirmados y registrados mediante :func:`registrar_compra`.

    Args:
        proveedor (Proveedor): Objeto del proveedor.
        path_imagen (str): Ruta del archivo de imagen del comprobante.
        como_compra (bool): Si es ``True`` se devuelve un objeto :class:`Compra`;
            en caso contrario, se retorna la lista de diccionarios de ítems.
        output_dir (str | Path | None): Directorio donde guardar la factura
            extraída en formato JSON. Se ignora si es ``None``.
        db_conn (sqlite3.Connection | None): Conexión a base de datos donde
            guardar la factura. Tiene prioridad sobre ``output_dir``. En ambos
            casos, si la factura es guardada, su identificador se registra en el
            log.
        omitidos (list[str] | None): Nombres de materias primas que deben
            omitirse durante el reconocimiento.
        selector (Callable[[dict], bool] | None): Función opcional que recibe
            cada ítem validado y devuelve ``True`` para incluirlo. Si retorna
            ``False`` el ítem se omite.

    Returns:
        tuple[list[dict], list[dict], dict] | tuple[Compra, list[dict], dict]:
            ``(items_validos, items_pendientes, meta)`` o ``(Compra,
            items_pendientes, meta)`` si ``como_compra`` es ``True``. ``meta``
            incluye información adicional del comprobante como proveedor,
            número, fecha y total.

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

    if not isinstance(proveedor, Proveedor) or not proveedor.nombre.strip():
        raise ValueError("El nombre del proveedor no puede estar vacío.")

    importer = importer or InvoiceImporter()

    omitidos = list(omitidos or [])
    metadata = {"archivo": path_imagen, "proveedor": proveedor.nombre}
    try:
        items_dict, faltantes, meta = importer.parse(path_imagen, omitidos)
    except ValueError:
        logger.exception("Error al interpretar la imagen", extra=metadata)
        raise

    pendientes: List[dict] = list(faltantes)
    try:
        items_validados = importer.validate(items_dict)
    except ValueError:
        logger.exception(
            "Error al convertir datos del comprobante",
            extra={"archivo": path_imagen, "proveedor": proveedor.nombre},
        )
        raise

    if selector is not None:
        items_validados = [i for i in items_validados if selector(i)]

    items_validados = importer.match(items_validados)

    destino = db_conn if db_conn is not None else output_dir
    factura = {
        "proveedor_id": proveedor.id,
        "proveedor": proveedor.nombre,
        "items": items_validados,
        "pendientes": pendientes,
    }
    if meta:
        factura.update(meta)
    importer.persist(factura, destino)

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
        return (
            Compra(proveedor_id=proveedor.id, items_compra=detalles),
            pendientes,
            meta,
        )

    return items_validados, pendientes, meta


def importar_factura_simple(
    proveedor: Proveedor, path_imagen: str, destino: Optional[object] = None
):
    """Importa una factura de forma simplificada.

    Este *helper* delega en :func:`registrar_compra_desde_imagen` utilizando
    valores por defecto para los parámetros menos utilizados.  Sólo requiere el
    proveedor, la ruta de la imagen del comprobante y, opcionalmente, un
    ``destino`` donde persistir la factura en formato JSON o en una base de
    datos SQLite.

    Args:
        proveedor: Proveedor al que pertenece la factura.
        path_imagen: Ruta al archivo de imagen del comprobante.
        destino: Directorio o conexión ``sqlite3.Connection`` donde guardar la
            factura.  Si es ``None`` la factura no se persiste.

    Returns:
        tuple[Compra, list[dict]]: El objeto :class:`Compra` generado a partir
        del comprobante y la lista de ítems pendientes.
    """

    db_conn = destino if isinstance(destino, sqlite3.Connection) else None
    output_dir = None if db_conn is not None else destino
    importer = InvoiceImporter()
    compra, pendientes, _ = registrar_compra_desde_imagen(
        proveedor,
        path_imagen,
        como_compra=True,
        output_dir=output_dir,
        db_conn=db_conn,
        omitidos=None,
        selector=None,
        importer=importer,
    )
    return compra, pendientes


def importar_comprobantes_masivos(proveedor: Proveedor, archivos: List[str]):
    """Procesa múltiples comprobantes y devuelve el estado por cada archivo.

    Para cada comprobante se intentará registrar la compra utilizando
    :func:`registrar_compra_desde_imagen`. En caso de error se registrará la
    excepción junto con metadatos del archivo y se devolverá un estado de
    error para ese comprobante.

    Args:
        proveedor (Proveedor): Objeto del proveedor.
        archivos (List[str]): Rutas de los comprobantes a importar.

    Returns:
        List[dict]: Lista de resultados por archivo con la forma
        ``{"archivo": str, "ok": bool, "compra": Compra | None, "pendientes": list, "error": str | None}``.
    """

    resultados = []
    for archivo in archivos:
        try:
            importer = InvoiceImporter()
            compra, pendientes, _ = registrar_compra_desde_imagen(
                proveedor, archivo, como_compra=True, importer=importer
            )
            resultados.append(
                {
                    "archivo": archivo,
                    "ok": True,
                    "compra": compra,
                    "pendientes": pendientes,
                }
            )
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.exception(
                "Error en importación masiva", extra={"archivo": archivo, "proveedor": proveedor.nombre}
            )
            resultados.append(
                {
                    "archivo": archivo,
                    "ok": False,
                    "error": str(exc),
                }
            )
    return resultados


def registrar_compra(proveedor: Proveedor, items_compra_detalle, fecha=None):
    """
    Registra una nueva compra con múltiples ítems y actualiza el stock de materias primas.
    Args:
        proveedor (Proveedor): Objeto del proveedor.
        items_compra_detalle (list): Lista de objetos CompraDetalle (ahora representando materias primas).
        fecha (str, optional): Fecha y hora de la compra en formato "YYYY-MM-DD HH:MM:SS". Si no se
            proporciona, se utilizará la fecha y hora actuales.
    Raises:
        ValueError: Si el proveedor está vacío o no hay ítems en la compra.
    Returns:
        Compra: El objeto Compra recién registrado.
    """
    if not isinstance(proveedor, Proveedor) or not proveedor.nombre.strip():
        raise ValueError("El nombre del proveedor no puede estar vacío.")
    if not items_compra_detalle:
        raise ValueError("La compra debe contener al menos un producto.")

    compras = cargar_compras()
    nueva_compra = Compra(
        proveedor_id=proveedor.id,
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


def eliminar_compra(compra_id: str) -> bool:
    """Elimina una compra existente, ajusta el stock y reexporta a Excel."""

    compras = cargar_compras()
    compra_obj = next((c for c in compras if c.id == compra_id), None)
    if not compra_obj:
        raise ValueError(
            f"Compra con ID '{compra_id}' no encontrada para eliminación."
        )

    procesados: list[CompraDetalle] = []
    try:
        for item in compra_obj.items_compra:
            actualizar_stock_materia_prima(item.producto_id, -item.cantidad)
            procesados.append(item)
    except Exception as e:  # pragma: no cover - rollback best effort
        for item in procesados:
            try:
                actualizar_stock_materia_prima(item.producto_id, item.cantidad)
            except Exception:
                logger.exception(
                    "Error al revertir stock al fallar eliminación de compra"
                )
        raise e

    nuevas_compras = [c for c in compras if c.id != compra_id]
    guardar_compras(nuevas_compras)
    exportar_compras_excel(nuevas_compras)
    return True


def listar_compras():
    """Retorna la lista completa de compras."""
    return cargar_compras()


def total_comprado():
    """Calcula y retorna el total de todas las compras registradas."""
    compras = listar_compras()
    return round(sum(c.total for c in compras), 2)

def obtener_compras_por_mes():
    """
    Calcula el total de compras agrupadas por mes y año.
    Retorna una lista de tuplas (mes_año, total_comprado_ese_mes) ordenada cronológicamente,
    con el total formateado con separador de miles y signo de moneda.
    Ejemplo: [('2023-01', 'Gs 50.000,00'), ('2023-02', 'Gs 75.000,00')]
    """
    compras = listar_compras()
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
    compras = listar_compras()
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
    compras = listar_compras()
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


__all__ = [
    "cargar_compras",
    "guardar_compras",
    "exportar_compras_excel",
    "registrar_materias_primas_faltantes",
    "registrar_compra_desde_imagen",
    "importar_factura_simple",
    "importar_comprobantes_masivos",
    "registrar_compra",
    "eliminar_compra",
    "listar_compras",
    "total_comprado",
    "obtener_compras_por_mes",
    "obtener_compras_por_semana",
    "obtener_compras_por_dia",
]


