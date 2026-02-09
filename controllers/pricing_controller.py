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


@dataclass(frozen=True)
class PlanVentaItem:
    producto_id: str
    unidades_previstas: float
    precio_venta_unitario: float
    margen_utilidad: float | None = None


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


def calcular_costo_fijo_unitario_proporcional(
    costos_fijos_periodo: float,
    plan_ventas: list[PlanVentaItem],
) -> dict[str, float]:
    """Distribuye los costos fijos del período según el valor de venta esperado."""
    if costos_fijos_periodo < 0:
        raise ValueError("Los costos fijos del período no pueden ser negativos.")
    if not plan_ventas:
        raise ValueError("El plan de ventas no puede estar vacío.")

    total_ventas = 0.0
    for item in plan_ventas:
        if item.unidades_previstas <= 0:
            raise ValueError("Las unidades previstas deben ser mayores a cero.")
        if item.precio_venta_unitario < 0:
            raise ValueError("El precio de venta unitario no puede ser negativo.")
        total_ventas += item.unidades_previstas * item.precio_venta_unitario

    if total_ventas <= 0:
        raise ValueError("El total de ventas esperadas debe ser mayor a cero.")

    costos_fijos_unitarios: dict[str, float] = {}
    for item in plan_ventas:
        peso = (item.unidades_previstas * item.precio_venta_unitario) / total_ventas
        costo_fijo_producto = costos_fijos_periodo * peso
        costos_fijos_unitarios[item.producto_id] = costo_fijo_producto / item.unidades_previstas

    return costos_fijos_unitarios


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


def calcular_precio_sugerido_proporcional(
    producto_id: str,
    costos_fijos_periodo: float,
    plan_ventas: list[PlanVentaItem],
    margen_utilidad: float | None,
    iva: float = 0.10,
) -> PrecioSugerido:
    """Calcula el precio de venta sugerido con costos fijos proporcionales."""
    if iva < 0:
        raise ValueError("El IVA no puede ser negativo.")

    costos_fijos_unitarios = calcular_costo_fijo_unitario_proporcional(
        costos_fijos_periodo,
        plan_ventas,
    )
    if producto_id not in costos_fijos_unitarios:
        raise ValueError("El producto no existe en el plan de ventas.")

    item_plan = next((item for item in plan_ventas if item.producto_id == producto_id), None)
    if not item_plan:
        raise ValueError("El producto no existe en el plan de ventas.")

    margen_producto = item_plan.margen_utilidad if item_plan.margen_utilidad is not None else margen_utilidad
    if margen_producto is None:
        raise ValueError("El margen de utilidad no puede estar vacío.")
    if margen_producto < 0:
        raise ValueError("El margen de utilidad no puede ser negativo.")

    costo_variable = calcular_costo_variable_unitario(producto_id)
    costo_fijo = costos_fijos_unitarios[producto_id]
    costo_total = costo_variable + costo_fijo
    precio_sin_impuestos = costo_total + (costo_total * margen_producto)
    precio_con_iva = precio_sin_impuestos * (1 + iva)

    return PrecioSugerido(
        costo_variable_unitario=costo_variable,
        costo_fijo_unitario=costo_fijo,
        costo_total_unitario=costo_total,
        precio_venta_sin_impuestos=precio_sin_impuestos,
        precio_venta_con_iva=precio_con_iva,
    )
