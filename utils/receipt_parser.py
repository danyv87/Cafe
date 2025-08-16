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


def _buscar_materia_prima(nombre: str):
    """Return ``MateriaPrima`` whose name matches ``nombre``.

    The search is case-insensitive and relies on ``listar_materias_primas``.
    ``None`` is returned if no match is found.
    """

    try:  # Import inside function to avoid heavy dependency at import time
        from controllers.materia_prima_controller import listar_materias_primas
    except Exception:  # pragma: no cover - fallback when controller unavailable
        return None

    nombre = nombre.strip().lower()
    for mp in listar_materias_primas():  # type: ignore[arg-type]
        if mp.nombre.strip().lower() == nombre:
            return mp
    return None


def _normalizar_items(raw_items: List[Dict]) -> List[Dict]:
    """Convert a list of raw dictionaries to the expected schema.

    ``raw_items`` is expected to contain at least the keys ``producto`` (or
    ``nombre_producto``), ``cantidad`` and ``precio`` (or ``costo_unitario``).

    The function maps product names to known "materias primas" using
    :func:`_buscar_materia_prima`. If a name cannot be matched a ``ValueError``
    is raised.
    """

    items: List[Dict] = []
    for raw in raw_items:
        nombre = raw.get("nombre_producto") or raw.get("producto")
        if not nombre:
            raise ValueError("Falta el nombre del producto en el comprobante")

        mp = _buscar_materia_prima(nombre)
        if not mp:
            raise ValueError(f"Materia prima '{nombre}' no encontrada")

        try:
            cantidad = float(raw.get("cantidad", 0))
            precio = float(raw.get("costo_unitario", raw.get("precio", 0)))
        except Exception as exc:  # pragma: no cover - propagates formatting errors
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


def parse_receipt_image(path_imagen: str) -> List[Dict]:
    """Parse a receipt image and return a list of item dictionaries.

    The function currently supports two backends:

    1. **JSON fallback** – If ``path_imagen`` ends with ``.json`` the file is
       loaded and assumed to contain the list of item dictionaries.
    2. **GPT based parser** – Delegates to :mod:`utils.gpt_receipt_parser` which
       uses the OpenAI API to process ``.jpeg``, ``.jpg`` or ``.png`` images.

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
        with open(path_imagen, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("El archivo JSON debe contener una lista de items")
        return _normalizar_items(data)

    # For images, attempt to use the GPT based parser
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

