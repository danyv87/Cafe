from __future__ import annotations

"""Utilities to interpret receipt images into structured purchase data.

This module acts as a thin wrapper over :func:`utils.ocr_utils.parse_invoice`
adding a small caching layer for lookups against existing ``MateriaPrima``
objects.  The :func:`parse_receipt_image` function returns two lists:

``items``
    List of items that could be matched with an existing materia prima.  Each
    element contains ``producto_id``, ``nombre_producto``, ``cantidad``,
    ``costo_unitario`` and ``descripcion_adicional``.

``faltantes``
    Items from the receipt that could not be matched.  They keep the original
    fields so the caller can decide how to handle them (e.g. offer to create a
    new materia prima).

The cache is invalidated with :func:`clear_cache` and stores lookups of materia
prima names to their objects so repeated calls do not hit disk every time.
"""

from typing import Dict, Iterable, List, Tuple

from .ocr_utils import parse_invoice

# Cache of ``nombre -> MateriaPrima`` for quick lookups.  We store the object so
# we can easily access its ``id`` and other attributes if needed.  The cache can
# be cleared when new materials are added via :func:`clear_cache`.
_MP_LOOKUP: Dict[str, object] | None = None


def _load_lookup() -> Dict[str, object]:
    """Return a mapping of materia prima names to objects.

    The lookup is cached because ``listar_materias_primas`` hits the JSON store
    on first call.  Subsequent calls reuse the in-memory cache until
    :func:`clear_cache` is invoked.
    """

    global _MP_LOOKUP
    if _MP_LOOKUP is None:
        from controllers.materia_prima_controller import listar_materias_primas

        _MP_LOOKUP = {
            mp.nombre.strip().lower(): mp for mp in listar_materias_primas()
        }
    return _MP_LOOKUP


def parse_receipt_image(
    path_imagen: str, omitidos: Iterable[str] | None = None
) -> Tuple[List[Dict], List[Dict]]:
    """Parse ``path_imagen`` and return items and missing entries.

    Parameters
    ----------
    path_imagen:
        Path to the receipt image.
    omitidos:
        Iterable of material names that should be ignored entirely from the
        result.  Comparison is case-insensitive.

    Returns
    -------
    tuple(list, list)
        ``(items, faltantes)`` where ``items`` contains dictionaries ready to be
        turned into :class:`models.compra_detalle.CompraDetalle` and ``faltantes``
        are items that could not be matched to an existing materia prima.
    """

    data = parse_invoice(path_imagen)
    items = []
    faltantes = []

    lookup = _load_lookup()
    omitidos_set = {o.strip().lower() for o in omitidos or []}

    for raw in data.get("items", []):
        nombre = (
            raw.get("nombre_producto")
            or raw.get("producto")
            or raw.get("descripcion")
            or ""
        ).strip()
        if not nombre or nombre.lower() in omitidos_set:
            continue

        try:
            cantidad = float(raw.get("cantidad", 0))
            costo_unitario = float(
                raw.get("costo_unitario") or raw.get("precio") or raw.get("costo")
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Cantidad o precio inválidos en el comprobante") from exc

        if cantidad <= 0 or costo_unitario <= 0:
            raise ValueError("Cantidad o precio inválidos en el comprobante")

        descripcion = raw.get("descripcion_adicional") or raw.get("descripcion") or ""

        key = nombre.lower()
        mp = lookup.get(key)
        if mp is not None:
            items.append(
                {
                    "producto_id": mp.id,
                    "nombre_producto": mp.nombre,
                    "cantidad": cantidad,
                    "costo_unitario": costo_unitario,
                    "descripcion_adicional": descripcion,
                }
            )
        else:
            # Preserve the relevant fields so the caller can later decide what to
            # do with this item (e.g. ask the user to create a new materia).
            faltantes.append(
                {
                    "nombre_producto": nombre,
                    "cantidad": cantidad,
                    "costo_unitario": costo_unitario,
                    "descripcion_adicional": descripcion,
                }
            )

    return items, faltantes


def clear_cache() -> None:
    """Clear internal caches used for materia prima lookups."""

    global _MP_LOOKUP
    _MP_LOOKUP = None


__all__ = ["parse_receipt_image", "clear_cache"]
