import json
import os
import sys  # Importar el módulo sys para PyInstaller
import logging
from models.producto import Producto

# Determinar la ruta base de la aplicación para compatibilidad con PyInstaller.
if getattr(sys, 'frozen', False):
    # Al estar congelado, usar la carpeta donde está el ejecutable
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # En ambiente de desarrollo, usar el directorio raíz del proyecto
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

DATA_PATH = os.path.join(BASE_PATH, "data", "productos.json")

# Asegurarse de que la carpeta 'data' exista
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def cargar_productos():
    """
    Carga la lista de productos desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    logger.debug(f"Intentando cargar productos desde: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        logger.debug(f"Archivo de productos no encontrado: {DATA_PATH}")
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Productos cargados (raw data): {data}")
            # Convierte los diccionarios cargados en objetos Producto
            return [Producto.from_dict(p) for p in data]
    except json.JSONDecodeError:
        # Maneja el caso de un archivo JSON vacío o malformado
        logger.error(
            f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía."
        )
        return []
    except Exception as e:
        logger.error(f"Error inesperado al cargar productos: {e}")
        return []


def guardar_productos(productos):
    """
    Guarda la lista de objetos Producto en el archivo JSON.
    """
    logger.debug(
        f"Intentando guardar {len(productos)} productos en: {DATA_PATH}"
    )
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        # Convierte los objetos Producto a diccionarios para guardarlos como JSON
        json.dump([p.to_dict() for p in productos], f, indent=4)
    logger.debug("Productos guardados con éxito.")


def validar_producto(nombre, precio_unitario):
    """
    Valida los datos de un producto (nombre y precio) antes de agregarlo o editarlo.
    Retorna True y un mensaje vacío si es válido, False y un mensaje de error en caso contrario.
    """
    if not nombre or not isinstance(nombre, str) or len(nombre.strip()) == 0:
        return False, "El nombre del producto no puede estar vacío."
    # Asegurarse de que el precio sea un número antes de la validación numérica
    if not isinstance(precio_unitario, (int, float)):
        return False, "El precio unitario debe ser un número."
    if precio_unitario <= 0:
        return False, "El precio unitario debe ser un número positivo."
    return True, ""


def agregar_producto(nombre, precio_unitario):
    """
    Agrega un nuevo producto a la lista y lo guarda.
    Realiza una validación básica antes de agregar.
    """
    es_valido, mensaje_error = validar_producto(nombre, precio_unitario)
    if not es_valido:
        raise ValueError(mensaje_error)  # Lanza un error si la validación falla

    productos = cargar_productos()
    nuevo_producto = Producto(nombre.strip(), precio_unitario)  # Elimina espacios en blanco del nombre
    productos.append(nuevo_producto)
    guardar_productos(productos)
    return nuevo_producto


def listar_productos():
    """
    Retorna la lista completa de productos.
    """
    return cargar_productos()


def obtener_producto_por_id(id_producto):
    """
    Busca y retorna un producto por su ID.
    Retorna None si el producto no es encontrado.
    """
    productos = cargar_productos()
    for producto in productos:
        if producto.id == id_producto:
            return producto
    return None


def editar_producto(id_producto, nuevo_nombre, nuevo_precio_unitario):
    """
    Edita un producto existente por su ID.
    Valida los nuevos datos y lanza un ValueError si el producto no se encuentra
    o si los datos no son válidos.
    """
    es_valido, mensaje_error = validar_producto(nuevo_nombre, nuevo_precio_unitario)
    if not es_valido:
        raise ValueError(mensaje_error)

    productos = cargar_productos()
    for i, producto in enumerate(productos):
        if producto.id == id_producto:
            productos[i].nombre = nuevo_nombre.strip()
            productos[i].precio_unitario = nuevo_precio_unitario
            guardar_productos(productos)
            return productos[i]  # Retorna el producto editado
    raise ValueError(f"Producto con ID '{id_producto}' no encontrado para edición.")


def eliminar_producto(id_producto):
    """
    Elimina un producto de la lista por su ID.
    Lanza un ValueError si el producto no se encuentra.
    """
    productos = cargar_productos()
    productos_original_count = len(productos)
    # Filtra la lista para crear una nueva sin el producto a eliminar
    productos = [p for p in productos if p.id != id_producto]

    if len(productos) == productos_original_count:
        raise ValueError(f"Producto con ID '{id_producto}' no encontrado para eliminación.")

    guardar_productos(productos)
    return True  # Retorna True si la eliminación fue exitosa


def calcular_costo_produccion_producto(producto_id):
    """
    Calcula el costo total de las materias primas necesarias para producir una unidad de un producto.
    Retorna el costo de producción o 0 si no hay receta o materias primas.
    """
    # Importaciones locales para evitar el ciclo de dependencia
    from controllers.recetas_controller import obtener_receta_por_producto_id
    from controllers.materia_prima_controller import obtener_materia_prima_por_id

    receta = obtener_receta_por_producto_id(producto_id)
    if not receta or not receta.ingredientes:
        return 0  # No hay receta o no tiene ingredientes, costo de producción es 0

    costo_total = 0
    for ingrediente in receta.ingredientes:
        mp_id = ingrediente["materia_prima_id"]
        cantidad_necesaria = ingrediente["cantidad_necesaria"]

        materia_prima = obtener_materia_prima_por_id(mp_id)
        if materia_prima:
            costo_total += (cantidad_necesaria * materia_prima.costo_unitario)
        else:
            logger.error(
                f"Advertencia: Materia prima con ID '{mp_id}' no encontrada para la receta del producto '{receta.nombre_producto}'. No se incluirá en el costo."
            )
            # Podrías lanzar un error aquí si quieres una validación más estricta
    return costo_total


def obtener_rentabilidad_productos():
    """
    Calcula la rentabilidad (ganancia y margen de beneficio) para cada producto.
    Retorna una lista de diccionarios con la información de rentabilidad.
    """
    productos = listar_productos()
    rentabilidad_data = []

    for p in productos:
        costo_produccion = calcular_costo_produccion_producto(p.id)
        ganancia = p.precio_unitario - costo_produccion
        margen_beneficio = (ganancia / p.precio_unitario * 100) if p.precio_unitario > 0 else 0

        rentabilidad_data.append({
            "producto_id": p.id,
            "nombre_producto": p.nombre,
            "precio_venta": p.precio_unitario,
            "costo_produccion": costo_produccion,
            "ganancia": ganancia,
            "margen_beneficio": margen_beneficio
        })
    return rentabilidad_data

# Faltante: función para obtener la receta por id de producto y exponerla aquí
def obtener_receta_por_producto_id(producto_id):
    """
    Provee la receta de un producto delegando al controlador de recetas.
    """
    from controllers.recetas_controller import obtener_receta_por_producto_id as obtener_receta
    return obtener_receta(producto_id)

# Faltante: función para obtener materia prima por id y exponerla aquí
def obtener_materia_prima_por_id(materia_prima_id):
    """
    Wrapper para exponer la función desde el controlador de materia prima.
    """
    from controllers.materia_prima_controller import obtener_materia_prima_por_id as _obtener_materia_prima_por_id
    return _obtener_materia_prima_por_id(materia_prima_id)