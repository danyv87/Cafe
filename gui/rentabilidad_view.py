import tkinter as tk
from tkinter import ttk # Importar ttk para Treeview
from controllers.productos_controller import obtener_rentabilidad_productos # Importa la nueva función

def mostrar_ventana_rentabilidad():
    ventana = tk.Toplevel()
    ventana.title("Rentabilidad de Productos")
    ventana.geometry("800x500") # Ajusta el tamaño para la tabla

    tk.Label(ventana, text="Rentabilidad de Productos", font=("Helvetica", 16, "bold")).pack(pady=20)

    # Crear un Treeview para mostrar los datos tabulados
    tree = ttk.Treeview(ventana, columns=("Producto", "Precio Venta", "Costo Producción", "Ganancia", "Margen Beneficio"), show="headings", height=15)

    # Definir las cabeceras de las columnas
    tree.heading("Producto", text="Producto")
    tree.heading("Precio Venta", text="Precio Venta (Gs)")
    tree.heading("Costo Producción", text="Costo Producción (Gs)")
    tree.heading("Ganancia", text="Ganancia (Gs)")
    tree.heading("Margen Beneficio", text="Margen Beneficio (%)")

    # Configurar el ancho y la alineación de las columnas
    tree.column("Producto", width=180, anchor="w")
    tree.column("Precio Venta", width=120, anchor="e")
    tree.column("Costo Producción", width=120, anchor="e")
    tree.column("Ganancia", width=120, anchor="e")
    tree.column("Margen Beneficio", width=100, anchor="e")

    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Obtener los datos de rentabilidad
    rentabilidad_data = obtener_rentabilidad_productos()

    if not rentabilidad_data:
        tree.insert("", tk.END, values=("No hay datos de rentabilidad para mostrar.", "", "", "", ""))
    else:
        for item in rentabilidad_data:
            # Formatear los valores numéricos para una mejor presentación
            precio_venta_formatted = f"{item['precio_venta']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            costo_produccion_formatted = f"{item['costo_produccion']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ganancia_formatted = f"{item['ganancia']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            margen_beneficio_formatted = f"{item['margen_beneficio']:.2f}".replace(".", ",") # Usar coma para decimales

            tree.insert("", tk.END, values=(
                item['nombre_producto'],
                precio_venta_formatted,
                costo_produccion_formatted,
                ganancia_formatted,
                margen_beneficio_formatted
            ))

    # Añadir un scrollbar al Treeview
    scrollbar = ttk.Scrollbar(ventana, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Empaquetar de nuevo para que el scrollbar funcione correctamente
