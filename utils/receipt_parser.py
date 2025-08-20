"""Utilities for parsing receipt images.

This module exposes :func:`parse_receipt_image` which takes the path to a
receipt image (or JSON file) and returns a list of dictionaries representing
purchase items. The implementation favours light dependencies so the function
tries to import parsers lazily and provides a JSON fallback for offline usage.
In unit tests the function is commonly patched to provide deterministic
results."""

from __future__ import annotations

import json
from typing import Dict, List


# Cache of normalised materia prima names to their objects. Populated lazily
# the first time :func:`_buscar_materia_prima` is invoked. ``None`` indicates
# that the cache has not been initialised yet.
_MATERIAS_PRIMAS_CACHE: Dict[str, "MateriaPrima"] | None = None


def clear_cache() -> None:
    """Clear internal cache of ``MateriaPrima`` objects.

    This is useful if the catalogue of materias primas changes at runtime and
    ensures subsequent lookups use fresh data.
    """

    global _MATERIAS_PRIMAS_CACHE
    _MATERIAS_PRIMAS_CACHE = None


def _buscar_materia_prima(nombre: str):
    """Return ``MateriaPrima`` whose name matches ``nombre``.

    The search is case-insensitive and relies on ``listar_materias_primas``.
    ``None`` is returned if no match is found. Results are cached so repeated
    lookups avoid querying the controller repeatedly.
    """

    global _MATERIAS_PRIMAS_CACHE

    try:  # Import inside function to avoid heavy dependency at import time
        from controllers.materia_prima_controller import listar_materias_primas
    except Exception:  # pragma: no cover - fallback when controller unavailable
        return None

    nombre_normalizado = nombre.strip().lower()

    # Populate cache on first use
    if _MATERIAS_PRIMAS_CACHE is None:
        _MATERIAS_PRIMAS_CACHE = {
            mp.nombre.strip().lower(): mp for mp in listar_materias_primas()  # type: ignore[arg-type]
        }

    return _MATERIAS_PRIMAS_CACHE.get(nombre_normalizado)


def _normalizar_items(raw_items: List[Dict]) -> List[Dict]:
    """Convert a list of raw dictionaries to the expected schema.

    ``raw_items`` is expected to contain at least the keys ``producto`` (or
    ``nombre_producto``), ``cantidad`` and ``precio`` (or ``costo_unitario``).

    The function maps product names to known "materias primas" using
    :func:`_buscar_materia_prima`. If a name cannot be matched the item is
    included in the result with ``producto_id`` set to ``None`` so callers can
    decide how to handle it.
    """

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

        try:
            cantidad = float(raw.get("cantidad", 0))
            precio = float(raw.get("costo_unitario", raw.get("precio", 0)))
        except Exception as exc:  # pragma: no cover - propagates formatting errors
            raise ValueError("Cantidad o precio inválidos en el comprobante") from exc

        items.append(
            {
                "producto_id": mp.id if mp else None,
                "nombre_producto": mp.nombre if mp else nombre,
                "cantidad": cantidad,
                "costo_unitario": precio,
                "descripcion_adicional": raw.get("descripcion_adicional", ""),
            }
        )
    return items


def parse_receipt_image(path_imagen: str) -> List[Dict]:
    """Parse a receipt image and return a list of item dictionaries.

    The function currently supports two backends:

    1. **JSON fallback** – If ``path_imagen`` ends with ``.json`` the file is
       loaded and assumed to contain the list of item dictionaries.
    2. **OCR based parser** – Delegates to :mod:`utils.gpt_receipt_parser` which
       uses Tesseract via ``pytesseract`` to process ``.jpeg``, ``.jpg`` or
       ``.png`` images.

    Returns
    -------
    list of dict
        Each dictionary contains ``producto_id``, ``nombre_producto``,
        ``cantidad`` and ``costo_unitario`` among other optional fields.
    """

    if not path_imagen:
        raise ValueError("path_imagen no puede estar vacío")

    # JSON files provide a convenient offline way of specifying receipt items
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

    # For images, attempt to use the OCR based parser
    try:  # Import lazily so environments without OpenAI dependencies still work
        from .gpt_receipt_parser import parse_receipt_image as gpt_parse
    except Exception as exc:  # pragma: no cover - unable to import backend
        raise NotImplementedError(
            "No hay backend disponible para procesar imágenes de recibo"
        ) from exc

    raw_items = gpt_parse(path_imagen)
    if not isinstance(raw_items, list):
        raise ValueError("La respuesta del backend de recibos es inválida")
    return _normalizar_items(raw_items)

