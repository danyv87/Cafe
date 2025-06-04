import tkinter as tk
from tkinter import ttk # Importar ttk para Treeview si fuera necesario en el futuro
from controllers.compras_controller import listar_compras, total_comprado # Importamos las funciones del controlador de compras

def mostrar_ventana_historial_compras():
    ventana = tk.Toplevel()
    ventana.title("Historial de Compras")
    ventana.geometry("650x500") # Ajusta el tamaño para mostrar más detalles

    tk.Label(ventana, text="Historial de Compras", font=("Helvetica", 16, "bold")).pack(pady=10)

    # Frame para el Listbox y su Scrollbar
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=90, yscrollcommand=scrollbar.set) # Ancho ajustado
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Carga las compras
    compras = listar_compras()
    if not compras:
        lista.insert(tk.END, "No hay compras registradas.")
    else:
        for c in compras:
            # Formatear el total de la compra
            total_compra_formateado = f"{c.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, "---------------------------------------------------------------------------------")
            lista.insert(tk.END, f"Compra ID: {c.id[:8]}... | Fecha: {c.fecha} | Proveedor: {c.proveedor} | Total Compra: Gs {total_compra_formateado}")
            lista.insert(tk.END, "  Items Comprados:")
            for item in c.items_compra:
                # Formatear el total de cada item y añadir la descripción si existe
                total_item_formateado = f"{item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                item_display_text = f"    - {item.cantidad} x {item.nombre_producto}"
                if item.descripcion_adicional: # Condición para mostrar la descripción
                    item_display_text += f" ({item.descripcion_adicional})"
                item_display_text += f" @ Gs {item.costo_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" = Gs {total_item_formateado}"
                lista.insert(tk.END, item_display_text)
            lista.insert(tk.END, "---------------------------------------------------------------------------------")

    # Muestra el total general de todas las compras
    total_general_compras = total_comprado()
    total_general_compras_formateado = f"{total_general_compras:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tk.Label(ventana, text=f"Total General Comprado: Gs {total_general_compras_formateado}", font=("Helvetica", 14, "bold"), fg="darkred").pack(pady=10)
