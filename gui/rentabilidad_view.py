import tkinter as tk
from tkinter import ttk
from controllers.productos_controller import obtener_rentabilidad_productos


def agregar_tab_rentabilidad(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con la rentabilidad de productos."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Rentabilidad")

    ttk.Label(frame, text="Rentabilidad de Productos", font=("Helvetica", 16, "bold")).pack(pady=20)

    tree = ttk.Treeview(
        frame,
        columns=("Producto", "Precio Venta", "Costo Producción", "Ganancia", "Margen Beneficio"),
        show="headings",
        height=15,
    )

    tree.heading("Producto", text="Producto")
    tree.heading("Precio Venta", text="Precio Venta (Gs)")
    tree.heading("Costo Producción", text="Costo Producción (Gs)")
    tree.heading("Ganancia", text="Ganancia (Gs)")
    tree.heading("Margen Beneficio", text="Margen Beneficio (%)")

    tree.column("Producto", width=180, anchor="w")
    tree.column("Precio Venta", width=120, anchor="e")
    tree.column("Costo Producción", width=120, anchor="e")
    tree.column("Ganancia", width=120, anchor="e")
    tree.column("Margen Beneficio", width=100, anchor="e")

    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    rentabilidad_data = obtener_rentabilidad_productos()

    if not rentabilidad_data:
        tree.insert("", tk.END, values=("No hay datos de rentabilidad para mostrar.", "", "", "", ""))
    else:
        for item in rentabilidad_data:
            precio_venta_formatted = f"{item['precio_venta']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            costo_produccion_formatted = f"{item['costo_produccion']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ganancia_formatted = f"{item['ganancia']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            margen_beneficio_formatted = f"{item['margen_beneficio']:.2f}".replace(".", ",")

            tree.insert(
                "",
                tk.END,
                values=(
                    item['nombre_producto'],
                    precio_venta_formatted,
                    costo_produccion_formatted,
                    ganancia_formatted,
                    margen_beneficio_formatted,
                ),
            )

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
