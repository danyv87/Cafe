import logging
from utils.json_utils import read_json, write_json
from models.proveedor import Proveedor
import config

DATA_PATH = config.get_data_path("proveedores.json")

logger = logging.getLogger(__name__)


def cargar_proveedores():
    data = read_json(DATA_PATH)
    return [Proveedor.from_dict(p) for p in data]


def guardar_proveedores(proveedores):
    write_json(DATA_PATH, [p.to_dict() for p in proveedores])


def validar_proveedor(nombre, contacto):
    if not nombre or not isinstance(nombre, str) or len(nombre.strip()) == 0:
        return False, "El nombre del proveedor no puede estar vacío."
    if not isinstance(contacto, str):
        return False, "El contacto debe ser texto."
    return True, ""


def agregar_proveedor(nombre, contacto=""):
    es_valido, mensaje = validar_proveedor(nombre, contacto)
    if not es_valido:
        raise ValueError(mensaje)
    proveedores = cargar_proveedores()
    nuevo = Proveedor(nombre, contacto)
    proveedores.append(nuevo)
    guardar_proveedores(proveedores)
    return nuevo


def listar_proveedores():
    return cargar_proveedores()


def obtener_proveedor_por_id(id_proveedor):
    proveedores = cargar_proveedores()
    for p in proveedores:
        if p.id == id_proveedor:
            return p
    return None


def editar_proveedor(id_proveedor, nuevo_nombre, nuevo_contacto=""):
    es_valido, mensaje = validar_proveedor(nuevo_nombre, nuevo_contacto)
    if not es_valido:
        raise ValueError(mensaje)
    proveedores = cargar_proveedores()
    for i, p in enumerate(proveedores):
        if p.id == id_proveedor:
            proveedores[i].nombre = nuevo_nombre.strip()
            proveedores[i].contacto = nuevo_contacto.strip()
            guardar_proveedores(proveedores)
            return proveedores[i]
    raise ValueError(f"Proveedor con ID '{id_proveedor}' no encontrado para edición.")


def eliminar_proveedor(id_proveedor):
    proveedores = cargar_proveedores()
    original = len(proveedores)
    proveedores = [p for p in proveedores if p.id != id_proveedor]
    if len(proveedores) == original:
        raise ValueError(f"Proveedor con ID '{id_proveedor}' no encontrado para eliminación.")
    guardar_proveedores(proveedores)
    return True
