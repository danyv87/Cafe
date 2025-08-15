import json
import logging
import os
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


def read_json(path):
    """Read JSON data from *path* and return the parsed content.

    If the file does not exist or contains invalid JSON, an empty list is
    returned. Any exception is logged.
    """
    try:
        if not os.path.exists(path):
            logger.debug(f"Archivo no encontrado: {path}")
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(
            f"Advertencia: El archivo {path} est\u00e1 vac\u00edo o malformado. Se devolver\u00e1 una lista vac\u00eda."
        )
    except Exception as e:
        logger.error(f"Error al leer {path}: {e}")
    return []


def crear_backup(path):
    """Crear una copia de seguridad del archivo indicado en data/backups."""
    try:
        if not os.path.exists(path):
            return
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        nombre = os.path.splitext(os.path.basename(path))[0]
        backup_dir = os.path.join("data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{nombre}-{timestamp}.json")
        shutil.copy(path, backup_path)
    except Exception as e:
        logger.error(f"Error al crear backup de {path}: {e}")


def write_json(path, data):
    """Serialize *data* to JSON and write it into *path*.

    Any exception during the write process is logged.
    """
    try:
        crear_backup(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error al escribir {path}: {e}")
        return False
    return True
