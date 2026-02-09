import logging
from datetime import datetime

import config
from utils.json_utils import read_json, write_json

logger = logging.getLogger(__name__)

DATA_PATH = config.get_data_path("planes_venta.json")


def cargar_planes_venta():
    """Carga la lista de planes de venta desde el archivo JSON."""
    planes = read_json(DATA_PATH)
    if not isinstance(planes, list):
        logger.warning("Formato inválido en planes_venta.json, se devuelve lista vacía.")
        return []
    return planes


def guardar_plan_venta(nombre, items):
    """Guarda o actualiza un plan de venta con sus ítems."""
    if not nombre or not isinstance(nombre, str):
        raise ValueError("El nombre del plan no puede estar vacío.")
    if not items:
        raise ValueError("El plan debe contener al menos un producto.")

    planes = cargar_planes_venta()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plan_existente = next((p for p in planes if p.get("nombre") == nombre), None)

    if plan_existente:
        plan_existente["items"] = items
        plan_existente["actualizado"] = timestamp
    else:
        planes.append({
            "nombre": nombre,
            "items": items,
            "actualizado": timestamp,
        })

    if not write_json(DATA_PATH, planes):
        raise ValueError("No se pudo guardar el plan de venta.")
    return True


def eliminar_plan_venta(nombre):
    """Elimina un plan de venta por su nombre."""
    planes = cargar_planes_venta()
    planes_filtrados = [p for p in planes if p.get("nombre") != nombre]

    if len(planes) == len(planes_filtrados):
        raise ValueError("No se encontró el plan de venta a eliminar.")

    if not write_json(DATA_PATH, planes_filtrados):
        raise ValueError("No se pudo eliminar el plan de venta.")
    return True
