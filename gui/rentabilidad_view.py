import tkinter as tk
from tkinter import ttk
from controllers.productos_controller import obtener_rentabilidad_productos


def agregar_tab_rentabilidad(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con el margen de contribución por producto."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Margen de Contribución")

    ttk.Label(
        frame,
        text="Margen de contribución por producto",
        font=("Helvetica", 16, "bold"),
    ).pack(pady=20)

    tree = ttk.Treeview(
        frame,
        columns=(
            "Producto",
            "Precio Venta",
            "Costo Producción",
            "Margen Contribucion",
            "Margen Contribucion Porcentaje",
        ),
        show="headings",
        height=15,
    )

    tree.heading("Producto", text="Producto")
    tree.heading("Precio Venta", text="Precio de venta (Gs) por unidad")
    tree.heading("Costo Producción", text="Costo variable unitario (Gs)")
    tree.heading("Margen Contribucion", text="Margen de contribución (Gs)")
    tree.heading("Margen Contribucion Porcentaje", text="Margen de contribución (%)")

    tree.column("Producto", width=180, anchor="w")
    tree.column("Precio Venta", width=120, anchor="e")
    tree.column("Costo Producción", width=120, anchor="e")
    tree.column("Margen Contribucion", width=150, anchor="e")
    tree.column("Margen Contribucion Porcentaje", width=160, anchor="e")

    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    rentabilidad_data = obtener_rentabilidad_productos()

    if not rentabilidad_data:
        tree.insert("", tk.END, values=("No hay datos de contribución para mostrar.", "", "", "", ""))
    else:
        for item in rentabilidad_data:
            precio_venta_formatted = f"{item['precio_venta_unitario']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            costo_produccion_formatted = f"{item['costo_produccion']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            margen_contribucion_formatted = f"{item['ganancia']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            margen_contribucion_pct_formatted = f"{item['margen_beneficio']:.2f}".replace(".", ",")

            tree.insert(
                "",
                tk.END,
                values=(
                    item['nombre_producto'],
                    precio_venta_formatted,
                    costo_produccion_formatted,
                    margen_contribucion_formatted,
                    margen_contribucion_pct_formatted,
                ),
            )

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
