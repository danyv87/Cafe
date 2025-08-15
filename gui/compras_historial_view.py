import tkinter as tk
from tkinter import ttk
from controllers.compras_controller import listar_compras, total_comprado


def agregar_tab_historial_compras(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con el historial de compras."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Historial de Compras")

    ttk.Label(frame, text="Historial de Compras", font=("Helvetica", 16, "bold")).pack(pady=10)

    frame_lista = ttk.Frame(frame)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=90, yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    compras = listar_compras()
    if not compras:
        lista.insert(tk.END, "No hay compras registradas.")
    else:
        for c in compras:
            total_compra_formateado = f"{c.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, "---------------------------------------------------------------------------------")
            lista.insert(
                tk.END,
                f"Compra ID: {c.id[:8]}... | Fecha: {c.fecha} | Proveedor: {c.proveedor} | Total Compra: Gs {total_compra_formateado}",
            )
            lista.insert(tk.END, "  Items Comprados:")
            for item in c.items_compra:
                total_item_formateado = f"{item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                item_display_text = f"    - {item.cantidad} x {item.nombre_producto}"
                if item.descripcion_adicional:
                    item_display_text += f" ({item.descripcion_adicional})"
                item_display_text += (
                    f" @ Gs {item.costo_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    + f" = Gs {total_item_formateado}"
                )
                lista.insert(tk.END, item_display_text)
            lista.insert(tk.END, "---------------------------------------------------------------------------------")

    total_general_compras = total_comprado()
    total_general_compras_formateado = f"{total_general_compras:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    ttk.Label(
        frame,
        text=f"Total General Comprado: Gs {total_general_compras_formateado}",
        font=("Helvetica", 14, "bold"),
        foreground="darkred",
    ).pack(pady=10)
