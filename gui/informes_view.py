import tkinter as tk
from controllers.tickets_controller import listar_tickets, total_vendido_tickets # Ahora importamos de tickets_controller

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
            lista.insert(tk.END, "----------------------------------------------------------------------")
            lista.insert(tk.END, f"Ticket ID: {t.id[:8]}... | Fecha: {t.fecha} | Cliente: {t.cliente} | Total Ticket: Gs {t.total:.0f}")
            lista.insert(tk.END, "  Productos:")
            for item in t.items_venta:
                lista.insert(tk.END, f"    - {item.cantidad} x {item.nombre_producto} @ Gs {item.precio_unitario:.0f} = Gs {item.total:.0f}")
            lista.insert(tk.END, "----------------------------------------------------------------------")

    # Muestra el total vendido de todos los tickets
    total_general = total_vendido_tickets()
    tk.Label(ventana, text=f"Total General Vendido: Gs {total_general:.0f}", font=("Helvetica", 14, "bold"), fg="darkgreen").pack(pady=10)
