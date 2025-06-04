import tkinter as tk
from tkinter import messagebox
from controllers.productos_controller import listar_productos
from controllers.tickets_controller import registrar_ticket  # Ahora importamos registrar_ticket
from models.venta_detalle import VentaDetalle  # Importamos VentaDetalle


def mostrar_ventana_ventas():
    ventana = tk.Toplevel()
    ventana.title("Registrar Venta (Ticket)")
    ventana.geometry("600x650")  # Aumenta el tamaño para acomodar mejor los elementos y scrollbars

    productos_disponibles = listar_productos()
    if not productos_disponibles:
        tk.Label(ventana, text="No hay productos cargados. Agregue al menos uno para registrar ventas.").pack(pady=20)
        return

    # Mapeo de nombre de producto a objeto Producto
    opciones_productos = {p.nombre: p for p in productos_disponibles}

    # --- Widgets de la Interfaz ---

    # Cliente
    tk.Label(ventana, text="Nombre del Cliente:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_cliente = tk.Entry(ventana, width=50)
    entry_cliente.pack()

    # Buscador producto
    tk.Label(ventana, text="Buscar producto:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_buscar = tk.Entry(ventana, width=50)
    entry_buscar.pack()

    tk.Label(ventana, text="Productos disponibles:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))

    # Frame para el Listbox de productos y su Scrollbar
    frame_productos_list = tk.Frame(ventana)
    frame_productos_list.pack(pady=5, fill=tk.BOTH, expand=True)

    scrollbar_productos = tk.Scrollbar(frame_productos_list, orient=tk.VERTICAL)
    lista_productos = tk.Listbox(frame_productos_list, height=6, width=60, yscrollcommand=scrollbar_productos.set,
                                 exportselection=False)
    scrollbar_productos.config(command=lista_productos.yview)

    scrollbar_productos.pack(side=tk.RIGHT, fill=tk.Y)
    lista_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Lista de productos agregados a la venta actual
    tk.Label(ventana, text="Productos en la venta actual:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))

    # Frame para el Listbox de la venta actual y su Scrollbar
    frame_venta_list = tk.Frame(ventana)
    frame_venta_list.pack(pady=5, fill=tk.BOTH, expand=True)

    scrollbar_venta = tk.Scrollbar(frame_venta_list, orient=tk.VERTICAL)
    lista_venta = tk.Listbox(frame_venta_list, height=8, width=60, yscrollcommand=scrollbar_venta.set)
    scrollbar_venta.config(command=lista_venta.yview)

    scrollbar_venta.pack(side=tk.RIGHT, fill=tk.Y)
    lista_venta.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(ventana, text="Cantidad:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_cantidad = tk.Entry(ventana, width=20)
    entry_cantidad.pack()

    label_total = tk.Label(ventana, text="Total: Gs 0", font=("Helvetica", 14, "bold"), fg="blue")
    label_total.pack(pady=15)

    # Lista para almacenar objetos VentaDetalle para el ticket actual
    venta_actual_items = []

    # --- Funciones ---

    def cargar_productos_disponibles(filtro=""):
        """
        Carga los productos disponibles en el Listbox, aplicando un filtro si se proporciona.
        """
        lista_productos.delete(0, tk.END)
        filtro = filtro.lower()
        productos_filtrados = []
        for p in productos_disponibles:
            if filtro in p.nombre.lower():
                productos_filtrados.append(p)

        if not productos_filtrados:
            lista_productos.insert(tk.END, "No se encontraron productos.")
        else:
            for p in productos_filtrados:
                lista_productos.insert(tk.END, f"ID: {p.id[:4]}... - {p.nombre} - Gs {p.precio_unitario:.0f}")

        if lista_productos.size() > 0:
            lista_productos.selection_set(0)  # Selecciona el primer elemento por defecto

    def on_buscar(event):
        """
        Evento que se dispara al escribir en el campo de búsqueda.
        Actualiza la lista de productos disponibles.
        """
        cargar_productos_disponibles(entry_buscar.get())

    def actualizar_total_ticket():
        """
        Calcula y actualiza el total de la venta actual (ticket).
        """
        total = sum(item.total for item in venta_actual_items)
        label_total.config(text=f"Total: Gs {total:.0f}")

    def agregar_producto_a_venta():
        """
        Agrega el producto seleccionado a la lista de la venta actual (como VentaDetalle).
        """
        try:
            seleccion_indices = lista_productos.curselection()
            if not seleccion_indices:
                messagebox.showwarning("Atención", "Seleccione un producto de la lista disponible.")
                return

            linea_seleccionada = lista_productos.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            producto_encontrado = None
            for p in productos_disponibles:
                if p.id.startswith(id_abrev):
                    producto_encontrado = p
                    break

            if not producto_encontrado:
                messagebox.showerror("Error", "No se pudo encontrar el producto original. Intente de nuevo.")
                return

            cantidad_str = entry_cantidad.get()
            if not cantidad_str.isdigit():
                messagebox.showerror("Error de Entrada", "La cantidad debe ser un número entero.")
                return

            cantidad = int(cantidad_str)
            if cantidad <= 0:
                messagebox.showerror("Error de Entrada", "La cantidad debe ser un número positivo.")
                return

            # Crea un objeto VentaDetalle y lo añade a la lista de ítems del ticket
            detalle_venta = VentaDetalle(
                producto_id=producto_encontrado.id,
                nombre_producto=producto_encontrado.nombre,
                cantidad=cantidad,
                precio_unitario=producto_encontrado.precio_unitario
            )
            venta_actual_items.append(detalle_venta)
            lista_venta.insert(tk.END,
                               f"{detalle_venta.nombre_producto} x {detalle_venta.cantidad} = Gs {detalle_venta.total:.0f}")

            actualizar_total_ticket()
            entry_cantidad.delete(0, tk.END)  # Limpia el campo de cantidad
            entry_cantidad.focus_set()  # Vuelve a poner el foco en la cantidad
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar producto al ticket: {e}")

    def generar_factura():
        """
        Genera el ticket completo y lo registra.
        """
        cliente = entry_cliente.get().strip()
        if not cliente:
            messagebox.showwarning("Atención", "Por favor, ingrese el nombre del cliente.")
            return
        if not venta_actual_items:
            messagebox.showwarning("Atención", "No hay productos en la venta actual.")
            return

        confirmar_factura = messagebox.askyesno(
            "Confirmar Factura",
            f"¿Desea generar la factura para '{cliente}' con un total de Gs {sum(item.total for item in venta_actual_items):.0f}?"
        )
        if not confirmar_factura:
            messagebox.showinfo("Cancelado", "Generación de factura cancelada.")
            return

        try:
            # Llama al controlador para registrar el ticket completo
            ticket_generado = registrar_ticket(cliente, venta_actual_items)

            messagebox.showinfo("Factura Generada",
                                f"Factura generada con éxito para {cliente}.\nTotal: Gs {ticket_generado.total:.0f}\nID Ticket: {ticket_generado.id[:8]}...")

            # Limpiar todo para una nueva venta
            venta_actual_items.clear()
            lista_venta.delete(0, tk.END)
            label_total.config(text="Total: Gs 0")
            entry_cliente.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_cliente.focus_set()  # Pone el foco en el campo del cliente
            cargar_productos_disponibles()  # Recarga la lista de productos disponibles
        except Exception as e:
            messagebox.showerror("Error al Generar Factura", f"No se pudo generar la factura.\nDetalle: {str(e)}")

    # --- Vinculación de Eventos y Carga Inicial ---
    entry_buscar.bind("<KeyRelease>", on_buscar)

    tk.Button(ventana, text="Agregar Producto a Venta", command=agregar_producto_a_venta, width=25).pack(pady=5)
    tk.Button(ventana, text="Generar Factura", command=generar_factura, width=25, bg="lightgreen", fg="black").pack(
        pady=10)

    cargar_productos_disponibles()  # Carga inicial de productos
