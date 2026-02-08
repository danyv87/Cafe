import calendar
from datetime import datetime
import tkinter as tk
from tkinter import ttk

from controllers.gastos_adicionales_controller import listar_gastos_adicionales
from controllers.pricing_controller import calcular_costo_variable_unitario
from controllers.productos_controller import listar_productos


def _obtener_costos_fijos_mes_actual() -> tuple[str, float]:
    hoy = datetime.now()
    periodo = hoy.strftime("%Y-%m")
    total = 0.0
    for gasto in listar_gastos_adicionales():
        try:
            fecha_gasto = datetime.strptime(gasto.fecha[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if fecha_gasto.strftime("%Y-%m") == periodo:
            total += gasto.monto
    return periodo, total


def _formatear_moneda(valor: float) -> str:
    return f"Gs {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _formatear_numero(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def agregar_tab_punto_equilibrio(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con el análisis de punto de equilibrio."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Punto de Equilibrio")

    ttk.Label(
        frame,
        text="Punto de equilibrio por producto",
        font=("Helvetica", 16, "bold"),
    ).pack(pady=15)

    periodo, costos_fijos = _obtener_costos_fijos_mes_actual()
    ttk.Label(
        frame,
        text=f"Costos fijos ({periodo}): {_formatear_moneda(costos_fijos)}",
        font=("Helvetica", 12, "bold"),
    ).pack(pady=5)

    tree = ttk.Treeview(
        frame,
        columns=(
            "Producto",
            "Precio Venta",
            "Costo Variable",
            "Margen Contribucion",
            "PE Mensual",
            "PE Diario",
        ),
        show="headings",
        height=15,
    )

    tree.heading("Producto", text="Producto")
    tree.heading("Precio Venta", text="Precio de venta (Gs)")
    tree.heading("Costo Variable", text="Costo variable unitario (Gs)")
    tree.heading("Margen Contribucion", text="Margen de contribución (Gs)")
    tree.heading("PE Mensual", text="Punto de equilibrio (u/mes)")
    tree.heading("PE Diario", text="Punto de equilibrio (u/día)")

    tree.column("Producto", width=180, anchor="w")
    tree.column("Precio Venta", width=120, anchor="e")
    tree.column("Costo Variable", width=150, anchor="e")
    tree.column("Margen Contribucion", width=150, anchor="e")
    tree.column("PE Mensual", width=170, anchor="e")
    tree.column("PE Diario", width=170, anchor="e")

    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    productos = listar_productos()
    if not productos:
        tree.insert("", tk.END, values=("No hay productos para analizar.", "", "", "", "", ""))
    else:
        dias_mes = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
        for producto in productos:
            precio_venta = producto.precio_unitario
            costo_variable = calcular_costo_variable_unitario(producto.id)
            margen_contribucion = precio_venta - costo_variable
            if margen_contribucion > 0 and costos_fijos > 0:
                pe_mensual = costos_fijos / margen_contribucion
                pe_diario = pe_mensual / dias_mes
                pe_mensual_str = _formatear_numero(pe_mensual)
                pe_diario_str = _formatear_numero(pe_diario)
            else:
                pe_mensual_str = "N/D"
                pe_diario_str = "N/D"

            tree.insert(
                "",
                tk.END,
                values=(
                    producto.nombre,
                    _formatear_moneda(precio_venta),
                    _formatear_moneda(costo_variable),
                    _formatear_moneda(margen_contribucion),
                    pe_mensual_str,
                    pe_diario_str,
                ),
            )

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
