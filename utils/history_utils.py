import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def guardar_version(path, data):
    """Guardar una versión del archivo original en data/history."""
    try:
        nombre = os.path.splitext(os.path.basename(path))[0]
        history_dir = os.path.join("data", "history", nombre)
        os.makedirs(history_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version_path = os.path.join(history_dir, f"{timestamp}.json")
        with open(version_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error al guardar versión de {path}: {e}")


def listar_versiones(path):
    """Listar las versiones disponibles de un archivo."""
    nombre = os.path.splitext(os.path.basename(path))[0]
    history_dir = os.path.join("data", "history", nombre)
    if not os.path.isdir(history_dir):
        return []
    archivos = [
        os.path.join(history_dir, f) for f in os.listdir(history_dir) if f.endswith(".json")
    ]
    return sorted(archivos)
