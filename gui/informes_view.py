import tkinter as tk
from tkinter import ttk
from controllers.tickets_controller import listar_tickets, total_vendido_tickets


def agregar_tab_historial_ventas(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con el historial de tickets de ventas."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Historial de Ventas")

    frame_lista = ttk.Frame(frame)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=80, yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tickets = listar_tickets()
    if not tickets:
        lista.insert(tk.END, "No hay tickets registrados.")
    else:
        for t in tickets:
            total_ticket_formateado = f"{t.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, "----------------------------------------------------------------------")
            lista.insert(
                tk.END,
                f"Ticket ID: {t.id[:8]}... | Fecha: {t.fecha} | Cliente: {t.cliente} | Total Ticket: Gs {total_ticket_formateado}",
            )
            lista.insert(tk.END, "  Productos:")
            for item in t.items_venta:
                total_item_formateado = f"{item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista.insert(
                    tk.END,
                    f"    - {item.cantidad} x {item.nombre_producto} @ Gs {item.precio_unitario:.0f} = Gs {total_item_formateado}",
                )
            lista.insert(tk.END, "----------------------------------------------------------------------")

    total_general = total_vendido_tickets()
    total_general_formateado = f"{total_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    ttk.Label(
        frame,
        text=f"Total General Vendido: Gs {total_general_formateado}",
        font=("Helvetica", 14, "bold"),
        foreground="darkgreen",
    ).pack(pady=10)
