import json
import os
from models.producto import Producto

DATA_PATH = "data/productos.json"

def cargar_productos():
    """
    Carga la lista de productos desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Convierte los diccionarios cargados en objetos Producto
            return [Producto.from_dict(p) for p in data]
    except json.JSONDecodeError:
        # Maneja el caso de un archivo JSON vacío o malformado
        print(f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía.")
        return []


def guardar_productos(productos):
    """
    Guarda la lista de objetos Producto en el archivo JSON.
    """
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        # Convierte los objetos Producto a diccionarios para guardarlos como JSON
        json.dump([p.to_dict() for p in productos], f, indent=4)

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
        raise ValueError(mensaje_error) # Lanza un error si la validación falla

    productos = cargar_productos()
    nuevo_producto = Producto(nombre.strip(), precio_unitario) # Elimina espacios en blanco del nombre
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
            return productos[i] # Retorna el producto editado
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
    return True # Retorna True si la eliminación fue exitosa
