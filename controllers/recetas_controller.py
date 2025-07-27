import json
import os
import logging
from models.receta import Receta
import config
from controllers.productos_controller import listar_productos, obtener_producto_por_id
from controllers.materia_prima_controller import listar_materias_primas, obtener_materia_prima_por_id

DATA_PATH = config.get_data_path("recetas.json")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def cargar_recetas():
    """
    Carga la lista de recetas desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    logger.debug(f"Intentando cargar recetas desde: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        logger.debug(f"Archivo de recetas no encontrado: {DATA_PATH}")
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Recetas cargadas (raw data): {data}")
            return [Receta.from_dict(r) for r in data]
    except json.JSONDecodeError:
        logger.error(
            f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía."
        )
        return []
    except Exception as e:
        logger.error(f"Error inesperado al cargar recetas: {e}")
        return []


def guardar_recetas(recetas):
    """
    Guarda la lista de objetos Receta en el archivo JSON.
    """
    logger.debug(f"Intentando guardar {len(recetas)} recetas en: {DATA_PATH}")
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in recetas], f, indent=4)
    logger.debug("Recetas guardadas con éxito.")


def validar_ingredientes_receta(ingredientes):
    """
    Valida que los ingredientes de una receta sean válidos (IDs de MP existentes y cantidades positivas).
    """
    if not isinstance(ingredientes, list):
        return False, "Los ingredientes deben ser una lista."
    if not ingredientes:
        return False, "Una receta debe tener al menos un ingrediente."

    materias_primas_existentes = {mp.id: mp for mp in listar_materias_primas()}

    for item in ingredientes:
        if not isinstance(item, dict):
            return False, "Cada ingrediente debe ser un diccionario."

        mp_id = item.get("materia_prima_id")
        cantidad_necesaria = item.get("cantidad_necesaria")

        if mp_id not in materias_primas_existentes:
            return False, f"Materia prima con ID '{mp_id}' no encontrada en el inventario."

        try:
            cantidad_necesaria = float(cantidad_necesaria)
            if cantidad_necesaria <= 0:
                return False, "La cantidad necesaria de un ingrediente debe ser un número positivo."
        except ValueError:
            return False, "La cantidad necesaria de un ingrediente debe ser un número válido."
    return True, ""


def validar_receta_completa(ingredientes, rendimiento):
    """
    Valida los ingredientes y el rendimiento de una receta.
    """
    es_valido_ingredientes, mensaje_ingredientes = validar_ingredientes_receta(ingredientes)
    if not es_valido_ingredientes:
        return False, mensaje_ingredientes

    if rendimiento is None or not isinstance(rendimiento, (int, float)) or rendimiento <= 0:
        return False, "El rendimiento de la receta debe ser un número positivo."

    return True, ""


def agregar_receta(producto_id, nombre_producto, ingredientes, rendimiento):
    """
    Agrega una nueva receta a la lista y la guarda.
    Valida que el producto exista, que los ingredientes sean válidos y el rendimiento.
    """
    # 1. Validar que el producto al que se asigna la receta exista
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        raise ValueError(f"Producto con ID '{producto_id}' no encontrado. No se puede crear la receta.")

    # 2. Validar los ingredientes y el rendimiento de la receta
    es_valido, mensaje_error = validar_receta_completa(ingredientes, rendimiento)
    if not es_valido:
        raise ValueError(mensaje_error)

    recetas = cargar_recetas()

    # Opcional: Verificar si ya existe una receta para este producto (una receta por producto)
    for r in recetas:
        if r.producto_id == producto_id:
            raise ValueError(f"Ya existe una receta para el producto '{nombre_producto}'. Edítela en su lugar.")

    nueva_receta = Receta(producto_id, nombre_producto, ingredientes, rendimiento)
    recetas.append(nueva_receta)
    guardar_recetas(recetas)
    return nueva_receta


def listar_recetas():
    """
    Retorna la lista completa de recetas.
    """
    return cargar_recetas()


def obtener_receta_por_producto_id(producto_id):
    """
    Busca y retorna una receta por el ID del producto al que pertenece.
    Retorna None si la receta no es encontrada.
    """
    recetas = cargar_recetas()
    for r in recetas:
        if r.producto_id == producto_id:
            return r
    return None


def editar_receta(receta_id, nuevos_ingredientes, nuevo_rendimiento):
    """
    Edita una receta existente por su ID.
    Valida los nuevos ingredientes y el rendimiento.
    """
    es_valido, mensaje_error = validar_receta_completa(nuevos_ingredientes, nuevo_rendimiento)
    if not es_valido:
        raise ValueError(mensaje_error)

    recetas = cargar_recetas()
    for i, r in enumerate(recetas):
        if r.id == receta_id:
            recetas[i].ingredientes = nuevos_ingredientes
            recetas[i].rendimiento = nuevo_rendimiento  # Actualizar el rendimiento
            guardar_recetas(recetas)
            return recetas[i]
    raise ValueError(f"Receta con ID '{receta_id}' no encontrada para edición.")


def eliminar_receta(receta_id):
    """
    Elimina una receta de la lista por su ID.
    """
    recetas = cargar_recetas()
    recetas_original_count = len(recetas)
    recetas = [r for r in recetas if r.id != receta_id]

    if len(recetas) == recetas_original_count:
        raise ValueError(f"Receta con ID '{receta_id}' no encontrada para eliminación.")

    guardar_recetas(recetas)
    return True
