"""Utilities for parsing receipt images.

This module exposes :func:`parse_receipt_image` which takes the path to a
receipt image (or JSON file) and yields dictionaries representing purchase
items. The implementation favours light dependencies so the function tries to
import parsers lazily and provides a JSON fallback for offline usage. In unit
tests the function is commonly patched to provide deterministic results.

The normalisation helpers operate in *streaming* mode: instead of materialising
intermediate lists, :func:`parse_receipt_image` yields tuples
``(item_validado, pendiente)`` one by one. Callers that need the full lists may
collect them explicitly while consumers interested in only a subset benefit
from reduced memory usage.
"""

from __future__ import annotations

import json
from typing import Dict, Iterable, Iterator, Tuple


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


def _normalizar_items(
    raw_items: Iterable[Dict], omitidos: Iterable[str] | None = None
) -> Iterator[Tuple[Dict | None, Dict | None]]:
    """Yield normalised items from ``raw_items``.

    ``raw_items`` is expected to contain at least the keys ``producto`` (or
    ``nombre_producto``), ``cantidad`` y ``precio`` (o ``costo_unitario``).

    Each iteration yields a tuple ``(item_validado, pendiente)``. Exactly one
    element of the tuple will be ``None`` depending on whether the raw element
    could be matched to an existing :class:`~models.materia_prima.MateriaPrima`.

    Args
    ----
    raw_items:
        Items obtenidos del backend del comprobante.
    omitidos:
        Iterable opcional de nombres de productos a ignorar.

    Yields
    ------
    tuple(dict | None, dict | None)
        ``item_validado`` junto con ``pendiente`` si no se encontró una materia
        prima asociada.
    """

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
            yield None, raw
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

        yield {
            "producto_id": mp.id,
            "nombre_producto": mp.nombre,
            "cantidad": cantidad,
            "costo_unitario": precio,
            "descripcion_adicional": descripcion,
        }, None


def parse_receipt_image(
    path_imagen: str, omitidos: Iterable[str] | None = None
) -> Iterator[Tuple[Dict | None, Dict | None]]:
    """Parse a receipt image and yield normalised items lazily.

    The function currently supports two backends:

    1. **JSON fallback** – If ``path_imagen`` ends with ``.json`` the file is
       loaded and assumed to contain the list of item dictionaries.
    2. **Gemini based parser** – Delegates to :mod:`utils.gemini_receipt_parser`
       which relies on the Gemini API to process ``.jpeg``, ``.jpg`` or
       ``.png`` images.

    Yields
    ------
    tuple(dict | None, dict | None)
        Tuplas ``(item_validado, pendiente)`` como las generadas por
        :func:`_normalizar_items`.
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
        return _normalizar_items(data, omitidos)

    # For images, attempt to use the Gemini based parser
    try:  # Import lazily so environments without OpenAI dependencies still work
        from .gemini_receipt_parser import parse_receipt_image as gemini_parse
    except Exception as exc:  # pragma: no cover - unable to import backend
        raise NotImplementedError(
            "No hay backend disponible para procesar imágenes de recibo"
        ) from exc

    raw_items = gemini_parse(path_imagen)
    if not isinstance(raw_items, list):
        raise ValueError("La respuesta del backend de recibos es inválida")
    return _normalizar_items(raw_items, omitidos)

