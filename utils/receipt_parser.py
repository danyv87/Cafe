"""Utilities for parsing receipt images with Tesseract OCR as primary backend.

If Tesseract falla o no reconoce nada útil, se intenta usar el backend GPT
(utils.gpt_receipt_parser).
"""

from __future__ import annotations
import json
from typing import Dict, List

# Cache de materias primas
_MATERIAS_PRIMAS_CACHE: Dict[str, "MateriaPrima"] | None = None


def clear_cache() -> None:
    global _MATERIAS_PRIMAS_CACHE
    _MATERIAS_PRIMAS_CACHE = None


def _buscar_materia_prima(nombre: str):
    global _MATERIAS_PRIMAS_CACHE
    try:
        from controllers.materia_prima_controller import listar_materias_primas
    except Exception:
        return None

    nombre_normalizado = nombre.strip().lower()
    if _MATERIAS_PRIMAS_CACHE is None:
        _MATERIAS_PRIMAS_CACHE = {
            mp.nombre.strip().lower(): mp for mp in listar_materias_primas()
        }
    return _MATERIAS_PRIMAS_CACHE.get(nombre_normalizado)


def _normalizar_items(raw_items: List[Dict]) -> List[Dict]:
    items: List[Dict] = []
    encontrados: Dict[str, "MateriaPrima"] = {}

    for raw in raw_items:
        nombre = raw.get("nombre_producto") or raw.get("producto")
        if not nombre:
            raise ValueError("Falta el nombre del producto en el comprobante")

        nombre_normalizado = nombre.strip().lower()
        mp = encontrados.get(nombre_normalizado)
        if mp is None:
            mp = _buscar_materia_prima(nombre)
            encontrados[nombre_normalizado] = mp
        if not mp:
            raise ValueError(f"Materia prima '{nombre}' no encontrada")

        try:
            cantidad = float(raw.get("cantidad", 0))
            precio = float(raw.get("costo_unitario", raw.get("precio", 0)))
        except Exception as exc:
            raise ValueError("Cantidad o precio inválidos en el comprobante") from exc

        items.append(
            {
                "producto_id": mp.id,
                "nombre_producto": mp.nombre,
                "cantidad": cantidad,
                "costo_unitario": precio,
                "descripcion_adicional": raw.get("descripcion_adicional", ""),
            }
        )
    return items


# ------------------------
# OCR con Tesseract
# ------------------------
def _ocr_tesseract(path_imagen: str) -> List[Dict]:
    from PIL import Image
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    img = Image.open(path_imagen)
    text = pytesseract.image_to_string(img, lang="spa")

    items = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            try:
                producto = " ".join(parts[:-2])
                cantidad = float(parts[-2].replace(",", "."))
                precio = float(parts[-1].replace(",", "."))
                items.append({"producto": producto, "cantidad": cantidad, "precio": precio})
            except ValueError:
                continue
    return items


def parse_receipt_image(path_imagen: str) -> List[Dict]:
    if not path_imagen:
        raise ValueError("path_imagen no puede estar vacío")

    # JSON directo
    if path_imagen.lower().endswith(".json"):
        try:
            with open(path_imagen, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise ValueError("Archivo JSON de recibo no encontrado") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("JSON de recibo inválido") from exc
        if not isinstance(data, list):
            raise ValueError("El archivo JSON debe contener una lista de items")
        return _normalizar_items(data)

    # Intentar primero con Tesseract
    try:
        raw_items = _ocr_tesseract(path_imagen)
        if raw_items:
            return _normalizar_items(raw_items)
    except Exception as e:
        print(f"OCR con Tesseract falló: {e}")

    # Si Tesseract no sirve, fallback a GPT
    try:
        from .gpt_receipt_parser import parse_receipt_image as gpt_parse
        raw_items = gpt_parse(path_imagen)
    except Exception as exc:
        raise NotImplementedError(
            "No hay backend disponible para procesar imágenes de recibo"
        ) from exc

    if not isinstance(raw_items, list):
        raise ValueError("La respuesta del backend de recibos es inválida")
    return _normalizar_items(raw_items)
