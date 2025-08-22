import logging
from utils.json_utils import read_json, write_json
from models.materia_prima import MateriaPrima
import config

DATA_PATH = config.get_data_path("materias_primas.json")

# Unidades permitidas para la materia prima
ALLOWED_UNIDADES = ["kg", "g", "l", "ml", "unidad"]

logger = logging.getLogger(__name__)

# Cache de materias primas para evitar lecturas repetidas del disco.
_MATERIAS_CACHE: list[MateriaPrima] | None = None
_CACHE_PATH: str | None = None


def clear_materias_cache() -> None:
    """Limpia el cache de materias primas.

    Esta función es útil en entornos de prueba para asegurar que cada test
    comience sin datos en memoria. También se invalida la ruta asociada al cache
    para que, en caso de cambiar ``DATA_PATH``, la próxima carga se realice
    desde el nuevo archivo.
    """
    global _MATERIAS_CACHE, _CACHE_PATH
    _MATERIAS_CACHE = None
    _CACHE_PATH = None


def cargar_materias_primas():
    """
    Carga la lista de materias primas desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    global _MATERIAS_CACHE, _CACHE_PATH

    if _MATERIAS_CACHE is not None and _CACHE_PATH == DATA_PATH:
        logger.debug("Retornando materias primas desde cache.")
        return _MATERIAS_CACHE

    logger.debug(f"Intentando cargar materias primas desde: {DATA_PATH}")
    data = read_json(DATA_PATH)
    logger.debug(f"Materias primas cargadas (raw data): {data}")
    _MATERIAS_CACHE = [MateriaPrima.from_dict(mp) for mp in data]
    _CACHE_PATH = DATA_PATH
    return _MATERIAS_CACHE


def guardar_materias_primas(materias_primas):
    """
    Guarda la lista de objetos MateriaPrima en el archivo JSON.
    """
    global _MATERIAS_CACHE, _CACHE_PATH

    logger.debug(
        f"Intentando guardar {len(materias_primas)} materias primas en: {DATA_PATH}"
    )
    write_json(DATA_PATH, [mp.to_dict() for mp in materias_primas])
    logger.debug("Materias primas guardadas con éxito.")

    # Actualizamos el cache para que refleje los datos persistidos.
    _MATERIAS_CACHE = materias_primas
    _CACHE_PATH = DATA_PATH


def validar_materia_prima(nombre, unidad_medida, costo_unitario, stock, stock_minimo=0):
    """
    Valida los datos de una materia prima.
    Retorna True si es válido, False y un mensaje de error en caso contrario.
    """
    if not nombre or not isinstance(nombre, str) or len(nombre.strip()) == 0:
        return False, "El nombre de la materia prima no puede estar vacío."
    if not unidad_medida or not isinstance(unidad_medida, str) or len(unidad_medida.strip()) == 0:
        return False, "La unidad de medida no puede estar vacía."
    if unidad_medida not in ALLOWED_UNIDADES:
        return False, f"Unidad de medida inválida. Opciones permitidas: {', '.join(ALLOWED_UNIDADES)}."
    if not isinstance(costo_unitario, (int, float)) or costo_unitario <= 0:
        return False, "El costo unitario debe ser un número positivo."
    if not isinstance(stock, (int, float)) or stock < 0:
        return False, "El stock debe ser un número no negativo."
    if not isinstance(stock_minimo, (int, float)) or stock_minimo < 0:
        return False, "El stock mínimo debe ser un número no negativo."
    if stock < stock_minimo:
        return False, "El stock inicial no puede ser menor al stock mínimo."
    return True, ""


def agregar_materia_prima(nombre, unidad_medida, costo_unitario, stock_inicial, stock_minimo=0):
    """
    Agrega una nueva materia prima a la lista y la guarda.
    """
    es_valido, mensaje_error = validar_materia_prima(nombre, unidad_medida, costo_unitario, stock_inicial, stock_minimo)
    if not es_valido:
        raise ValueError(mensaje_error)

    materias_primas = cargar_materias_primas()
    nueva_materia_prima = MateriaPrima(
        nombre.strip(),
        unidad_medida.strip(),
        costo_unitario,
        stock_inicial,
        stock_minimo
    )
    materias_primas.append(nueva_materia_prima)
    guardar_materias_primas(materias_primas)
    return nueva_materia_prima


def listar_materias_primas():
    """
    Retorna la lista completa de materias primas.
    """
    return cargar_materias_primas()


def materias_con_stock_bajo():
    """Retorna la lista de materias primas cuyo stock actual es menor o igual al stock mínimo."""
    materias = cargar_materias_primas()
    return [mp for mp in materias if mp.stock <= mp.stock_minimo]


def obtener_materia_prima_por_id(id_materia_prima):
    """
    Busca y retorna una materia prima por su ID.
    Retorna None si la materia prima no es encontrada.
    """
    materias_primas = cargar_materias_primas()
    for mp in materias_primas:
        if mp.id == id_materia_prima:
            return mp
    return None


def editar_materia_prima(id_materia_prima, nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario, nuevo_stock, nuevo_stock_minimo=0):
    """
    Edita una materia prima existente por su ID.
    """
    es_valido, mensaje_error = validar_materia_prima(nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario,
                                                     nuevo_stock, nuevo_stock_minimo)
    if not es_valido:
        raise ValueError(mensaje_error)

    materias_primas = cargar_materias_primas()
    for i, mp in enumerate(materias_primas):
        if mp.id == id_materia_prima:
            materias_primas[i].nombre = nuevo_nombre.strip()
            materias_primas[i].unidad_medida = nueva_unidad_medida.strip()
            materias_primas[i].costo_unitario = nuevo_costo_unitario
            materias_primas[i].stock = nuevo_stock
            materias_primas[i].stock_minimo = nuevo_stock_minimo
            guardar_materias_primas(materias_primas)
            return materias_primas[i]
    raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para edición.")


def eliminar_materia_prima(id_materia_prima):
    """
    Elimina una materia prima de la lista por su ID.
    """
    materias_primas = cargar_materias_primas()
    materias_primas_original_count = len(materias_primas)
    materias_primas = [mp for mp in materias_primas if mp.id != id_materia_prima]

    if len(materias_primas) == materias_primas_original_count:
        raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para eliminación.")

    guardar_materias_primas(materias_primas)
    return True


def actualizar_stock_materia_prima(id_materia_prima, cantidad_cambio):
    """
    Actualiza el stock de una materia prima.
    Args:
        id_materia_prima (str): ID de la materia prima a actualizar.
        cantidad_cambio (float): Cantidad a sumar (para compras) o restar (para ventas).
    Raises:
        ValueError: Si la materia prima no se encuentra o el stock resultante es negativo.
    """
    materias_primas = cargar_materias_primas()
    materia_prima_encontrada = None
    for i, mp in enumerate(materias_primas):
        if mp.id == id_materia_prima:
            materia_prima_encontrada = mp
            break

    if not materia_prima_encontrada:
        raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para actualizar stock.")

    nuevo_stock = materia_prima_encontrada.stock + cantidad_cambio
    if nuevo_stock < 0:
        raise ValueError(
            f"Stock insuficiente para '{materia_prima_encontrada.nombre}'. Se intenta reducir el stock a {nuevo_stock}, pero solo hay {materia_prima_encontrada.stock}.")

    materias_primas[i].stock = nuevo_stock
    guardar_materias_primas(materias_primas)
    return materias_primas[i]


def establecer_stock_materia_prima(id_materia_prima, nuevo_stock_absoluto):
    """
    Establece el stock de una materia prima a un valor absoluto específico.
    Calcula la diferencia y llama a actualizar_stock_materia_prima.
    Args:
        id_materia_prima (str): ID de la materia prima a actualizar.
        nuevo_stock_absoluto (int): El nuevo valor de stock deseado.
    Raises:
        ValueError: Si la materia prima no se encuentra o el nuevo stock absoluto es negativo.
    """
    if not isinstance(nuevo_stock_absoluto, int) or nuevo_stock_absoluto < 0:
        raise ValueError("El stock absoluto debe ser un número entero no negativo.")

    materia_prima = obtener_materia_prima_por_id(id_materia_prima)
    if not materia_prima:
        raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para establecer stock.")

    cantidad_actual = materia_prima.stock
    cantidad_cambio = nuevo_stock_absoluto - cantidad_actual

    # Reutilizamos la lógica de actualización de stock.
    # No necesitamos verificar si el stock resultante es negativo aquí,
    # ya que actualizar_stock_materia_prima ya lo hace.
    return actualizar_stock_materia_prima(id_materia_prima, cantidad_cambio)

