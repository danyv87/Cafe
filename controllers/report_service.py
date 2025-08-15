"""Utilities to build numeric reports for the application.

This module centralises the logic to aggregate different financial
concepts (ventas, compras y gastos adicionales).  The functions defined
here return plain numeric dictionaries in the form ``{periodo: monto}``
without any formatting so the presentation layer can decide how to
display the values.

Each public function accepts a ``periodo`` argument which can be one of
``"mensual"``, ``"semanal"`` o ``"diario"``.  The keys of the returned
dictionary follow the formats ``YYYY-MM`` for monthly aggregation,
``YYYY-WNN`` for weekly aggregation (ISO week number) and ``YYYY-MM-DD``
for daily aggregation.

Example:

>>> ventas_agrupadas("mensual")
{"2024-01": 150000, "2024-02": 120000}

The helpers defined in this file can easily be reused to extend the
reports with new data sources – see ``controllers/__init__.py`` for
documentation on how to do that.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable, Dict, Callable

# Importamos las funciones de carga desde los controladores existentes.
from .tickets_controller import cargar_tickets
from .compras_controller import cargar_compras
from .gastos_adicionales_controller import cargar_gastos_adicionales


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _parse_fecha(value) -> datetime | None:
    """Convierte ``value`` en ``datetime``.

    Las fechas se almacenan como ``str`` en los JSON, pero algunos
    modelos podrían guardarlas como ``datetime`` directamente.  Si la
    conversión falla se devuelve ``None`` y el registro será ignorado.
    """

    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            # Solo tomamos los primeros 19 caracteres para evitar problemas
            # con formatos que incluyan microsegundos u otra información.
            return datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    return None


def _clave_periodo(fecha: datetime, periodo: str) -> str:
    """Genera la clave del diccionario según ``periodo``."""

    if periodo == "mensual":
        return fecha.strftime("%Y-%m")
    if periodo == "semanal":
        year, week, _ = fecha.isocalendar()
        return f"{year}-W{week:02d}"
    if periodo == "diario":
        return fecha.strftime("%Y-%m-%d")
    raise ValueError(f"Periodo '{periodo}' no soportado")


def _agrupar(
    items: Iterable,
    periodo: str,
    attr_fecha: str,
    attr_valor: str,
) -> Dict[str, float]:
    """Agrupa ``items`` por ``periodo`` sumando ``attr_valor``.

    ``attr_fecha`` debe ser el nombre del atributo que contiene la fecha y
    ``attr_valor`` el nombre del atributo numérico a sumar.
    """

    acumulado: Dict[str, float] = defaultdict(float)

    for item in items:
        fecha = _parse_fecha(getattr(item, attr_fecha, None))
        if not fecha:
            # Si la fecha es inválida simplemente ignoramos el registro
            # para mantener la integridad del reporte.
            continue
        clave = _clave_periodo(fecha, periodo)
        acumulado[clave] += float(getattr(item, attr_valor, 0.0))

    # Se devuelve un diccionario ordenado por clave para facilitar su uso
    # en las vistas.
    return dict(sorted(acumulado.items()))


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------


def ventas_agrupadas(periodo: str = "mensual") -> Dict[str, float]:
    """Retorna las ventas agrupadas por ``periodo``.

    Parameters
    ----------
    periodo: str
        Puede ser ``"mensual"``, ``"semanal"`` o ``"diario"``.

    Returns
    -------
    Dict[str, float]
        Diccionario ``{periodo: monto}`` sin formatear.
    """

    tickets = cargar_tickets()
    return _agrupar(tickets, periodo, "fecha", "total")


def compras_agrupadas(periodo: str = "mensual") -> Dict[str, float]:
    """Retorna las compras agrupadas por ``periodo``."""

    compras = cargar_compras()
    return _agrupar(compras, periodo, "fecha", "total")


def gastos_adicionales_agrupados(periodo: str = "mensual") -> Dict[str, float]:
    """Retorna los gastos adicionales agrupados por ``periodo``."""

    gastos = cargar_gastos_adicionales()
    return _agrupar(gastos, periodo, "fecha", "monto")


__all__ = [
    "ventas_agrupadas",
    "compras_agrupadas",
    "gastos_adicionales_agrupados",
]

