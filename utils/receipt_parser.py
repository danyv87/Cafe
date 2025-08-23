"""Utilities for parsing receipt images.

This module exposes :func:`parse_receipt_image` which takes the path to a
receipt image (or JSON file) and returns a list of dictionaries representing
purchase items. The implementation favours light dependencies so the function
tries to import parsers lazily and provides a JSON fallback for offline usage.
In unit tests the function is commonly patched to provide deterministic
results."""

from __future__ import annotations

import json
from typing import Dict, List, Tuple


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


def _buscar_materia_prima(nombre: str, threshold: float = 0.85):
    """Return ``MateriaPrima`` whose name approximately matches ``nombre``.

    The search is case-insensitive and relies on ``listar_materias_primas``.
    ``None`` is returned if no match is found. Results are cached so repeated
    lookups avoid querying the controller repeatedly. When an exact match is
    not found, a secondary fuzzy search is performed using
    :func:`difflib.get_close_matches`. ``threshold`` specifies the minimum
    similarity ratio required to accept a fuzzy match.
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

    mp = _MATERIAS_PRIMAS_CACHE.get(nombre_normalizado)
    if mp is not None:
        return mp

    # Fallback to fuzzy matching when an exact key lookup fails
    from difflib import get_close_matches

    closest = get_close_matches(
        nombre_normalizado, _MATERIAS_PRIMAS_CACHE.keys(), n=1, cutoff=threshold
    )
    if closest:
        return _MATERIAS_PRIMAS_CACHE[closest[0]]
    return None


def _normalizar_items(
    raw_items: List[Dict], omitidos: List[str] | None = None
) -> Tuple[List[Dict], List[Dict]]:
    """Convert a list of raw dictionaries to the expected schema.

    ``raw_items`` is expected to contain at least the keys ``producto`` (or
    ``nombre_producto``), ``cantidad`` y ``precio`` (o ``costo_unitario``).

    Args
    ----
    raw_items:
        Items obtenidos del backend del comprobante.
    omitidos:
        Lista opcional de nombres de productos a ignorar.

    Returns
    -------
    tuple(list, list)
        Una tupla con ``items`` normalizados y ``faltantes`` que no pudieron
        emparejarse con una materia prima.
    """

    items: List[Dict] = []
    faltantes: List[Dict] = []
    encontrados: Dict[str, "MateriaPrima"] = {}
    omitidos_norm = {n.strip().lower() for n in (omitidos or [])}

    for raw in raw_items:
        nombre = (
            raw.get("nombre_producto")
            or raw.get("producto")
            or raw.get("descripcion")
            or raw.get("description")
        )
        if not nombre:
            raise ValueError("Falta el nombre del producto en el comprobante")

        nombre_normalizado = nombre.strip().lower()
        if nombre_normalizado in omitidos_norm:
            continue

        mp = encontrados.get(nombre_normalizado)
        if mp is None:
            mp = _buscar_materia_prima(nombre)
            encontrados[nombre_normalizado] = mp
        if not mp:
            faltantes.append(raw)
            continue

        try:
            cantidad = float(raw.get("cantidad", 0))
            precio_valor = raw.get("costo_unitario")
            if precio_valor in (None, ""):
                precio_valor = raw.get("precio")
            if precio_valor in (None, ""):
                precio_valor = raw.get("precio_unitario")
            if precio_valor in (None, ""):
                precio_valor = raw.get("subtotal", 0)
            precio = float(precio_valor)
        except Exception as exc:  # pragma: no cover - propagates formatting errors
            raise ValueError("Cantidad o precio inválidos en el comprobante") from exc

        descripcion = raw.get("descripcion_adicional")
        if descripcion is None:
            extras = {
                k: v
                for k, v in raw.items()
                if k
                not in {
                    "nombre_producto",
                    "producto",
                    "descripcion",
                    "description",
                    "cantidad",
                    "precio",
                    "costo_unitario",
                    "precio_unitario",
                    "subtotal",
                    "descripcion_adicional",
                }
            }
            if extras:
                descripcion = ", ".join(f"{k}: {v}" for k, v in extras.items())
        if not descripcion:
            descripcion = ""

        items.append(
            {
                "producto_id": mp.id,
                "nombre_producto": mp.nombre,
                "cantidad": cantidad,
                "costo_unitario": precio,
                "descripcion_adicional": descripcion,
            }
        )
    return items, faltantes


def parse_receipt_image(
    path_imagen: str, omitidos: List[str] | None = None
) -> Tuple[List[Dict], List[Dict], Dict[str, object]]:
    """Parse a receipt image and return a tuple of item dictionaries.

    The function currently supports two backends:

    1. **JSON fallback** – If ``path_imagen`` ends with ``.json`` the file is
       loaded and assumed to contain either a list of items or a dictionary
       containing an ``items`` list and optional metadata.
    2. **Gemini based parser** – Delegates to :mod:`utils.gemini_receipt_parser`
       which relies on the Gemini API to process ``.jpeg``, ``.jpg`` or
       ``.png`` images.  The backend may return either the raw list of items or
       a dictionary with ``items`` and metadata.

    Returns
    -------
    tuple(list, list, dict)
        ``items`` normalizados, ``faltantes`` cuyos nombres no coincidieron con
        ninguna materia prima conocida y ``meta`` con información adicional del
        comprobante (por ejemplo ``proveedor`` o ``total``).
    """

    if not path_imagen:
        raise ValueError("path_imagen no puede estar vacío")

    meta: Dict[str, object] = {}

    # JSON files provide a convenient offline way of specifying receipt items
    if path_imagen.lower().endswith(".json"):
        try:
            with open(path_imagen, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise ValueError("Archivo JSON de recibo no encontrado") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("JSON de recibo inválido") from exc

        raw_items: List[Dict]
        if isinstance(data, dict):
            raw_items = data.get("items", [])
            if not isinstance(raw_items, list):
                raise ValueError("El archivo JSON debe contener una lista de items")
            meta = {
                "proveedor": data.get("proveedor"),
                "numero": data.get("numero_comprobante") or data.get("numero"),
                "fecha": data.get("fecha"),
                "total": data.get("total"),
            }
        elif isinstance(data, list):
            raw_items = data
        else:
            raise ValueError("El archivo JSON debe contener una lista de items")

        items, faltantes = _normalizar_items(raw_items, omitidos)
        return items, faltantes, meta

    # For images, attempt to use the Gemini based parser
    try:  # Import lazily so environments without OpenAI dependencies still work
        from .gemini_receipt_parser import parse_receipt_image as gemini_parse
    except Exception as exc:  # pragma: no cover - unable to import backend
        raise NotImplementedError(
            "No hay backend disponible para procesar imágenes de recibo"
        ) from exc

    raw = gemini_parse(path_imagen)
    raw_items: List[Dict]
    if isinstance(raw, dict):
        raw_items = raw.get("items", [])  # type: ignore[assignment]
        if not isinstance(raw_items, list):
            raise ValueError("La respuesta del backend de recibos es inválida")
        meta = {
            "proveedor": raw.get("proveedor"),
            "numero": raw.get("numero_comprobante") or raw.get("numero"),
            "fecha": raw.get("fecha"),
            "total": raw.get("total"),
        }
    elif isinstance(raw, list):
        raw_items = raw
    else:
        raise ValueError("La respuesta del backend de recibos es inválida")

    items, faltantes = _normalizar_items(raw_items, omitidos)
    return items, faltantes, meta

