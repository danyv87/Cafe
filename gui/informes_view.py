import tkinter as tk
from controllers.tickets_controller import listar_tickets, total_vendido_tickets # Importamos de tickets_controller

def mostrar_ventana_informes():
    ventana = tk.Toplevel()
    ventana.title("Historial de Ventas (Tickets)") # Título actualizado
    ventana.geometry("600x500") # Ajusta el tamaño para mostrar más detalles

    # Frame para el Listbox y su Scrollbar
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=80, yscrollcommand=scrollbar.set) # Ancho ajustado
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Carga los tickets en lugar de ventas individuales
    tickets = listar_tickets()
    if not tickets:
        lista.insert(tk.END, "No hay tickets registrados.")
    else:
        for t in tickets:
            # Formatear el total del ticket
            total_ticket_formateado = f"{t.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, "----------------------------------------------------------------------")
            lista.insert(tk.END, f"Ticket ID: {t.id[:8]}... | Fecha: {t.fecha} | Cliente: {t.cliente} | Total Ticket: Gs {total_ticket_formateado}")
            lista.insert(tk.END, "  Productos:")
            for item in t.items_venta:
                # Formatear el total de cada item
                total_item_formateado = f"{item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista.insert(tk.END, f"    - {item.cantidad} x {item.nombre_producto} @ Gs {item.precio_unitario:.0f} = Gs {total_item_formateado}")
            lista.insert(tk.END, "----------------------------------------------------------------------")

    # Muestra el total vendido de todos los tickets
    total_general = total_vendido_tickets()
    # Formatear el total general
    total_general_formateado = f"{total_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tk.Label(ventana, text=f"Total General Vendido: Gs {total_general_formateado}", font=("Helvetica", 14, "bold"), fg="darkgreen").pack(pady=10)
