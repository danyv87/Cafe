from __future__ import annotations

from dataclasses import dataclass

from controllers.productos_controller import calcular_costo_produccion_producto
from controllers.recetas_controller import obtener_receta_por_producto_id


@dataclass(frozen=True)
class PrecioSugerido:
    costo_variable_unitario: float
    costo_fijo_unitario: float
    costo_total_unitario: float
    precio_venta_sin_impuestos: float
    precio_venta_con_iva: float


def calcular_costo_variable_unitario(producto_id: str) -> float:
    """Calcula el costo variable unitario (CV) usando receta y materias primas."""
    receta = obtener_receta_por_producto_id(producto_id)
    rendimiento = (
        receta.rendimiento if receta and receta.rendimiento and receta.rendimiento > 0 else 1
    )
    costo_produccion_total = calcular_costo_produccion_producto(producto_id)
    return costo_produccion_total / rendimiento


def calcular_costo_fijo_unitario(costos_fijos_periodo: float, unidades_previstas: float) -> float:
    """Distribuye los costos fijos del período según las unidades previstas (UP)."""
    if unidades_previstas <= 0:
        raise ValueError("Las unidades previstas (UP) deben ser mayores a cero.")
    return costos_fijos_periodo / unidades_previstas


def calcular_costo_total_unitario(
    producto_id: str,
    costos_fijos_periodo: float,
    unidades_previstas: float,
) -> float:
    """Calcula el costo total unitario (CT = CV + CF/UP)."""
    costo_variable = calcular_costo_variable_unitario(producto_id)
    costo_fijo = calcular_costo_fijo_unitario(costos_fijos_periodo, unidades_previstas)
    return costo_variable + costo_fijo


def calcular_precio_sugerido(
    producto_id: str,
    costos_fijos_periodo: float,
    unidades_previstas: float,
    margen_utilidad: float,
    iva: float = 0.10,
) -> PrecioSugerido:
    """Calcula el precio de venta sugerido usando MU e IVA."""
    if margen_utilidad < 0:
        raise ValueError("El margen de utilidad no puede ser negativo.")
    if iva < 0:
        raise ValueError("El IVA no puede ser negativo.")

    costo_variable = calcular_costo_variable_unitario(producto_id)
    costo_fijo = calcular_costo_fijo_unitario(costos_fijos_periodo, unidades_previstas)
    costo_total = costo_variable + costo_fijo
    precio_sin_impuestos = costo_total + (costo_total * margen_utilidad)
    precio_con_iva = precio_sin_impuestos * (1 + iva)

    return PrecioSugerido(
        costo_variable_unitario=costo_variable,
        costo_fijo_unitario=costo_fijo,
        costo_total_unitario=costo_total,
        precio_venta_sin_impuestos=precio_sin_impuestos,
        precio_venta_con_iva=precio_con_iva,
    )
