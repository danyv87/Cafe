import tkinter as tk
from tkinter import messagebox
from controllers.productos_controller import listar_productos
from controllers.tickets_controller import registrar_ticket
from models.venta_detalle import VentaDetalle
from controllers.recetas_controller import obtener_receta_por_producto_id
from controllers.materia_prima_controller import obtener_materia_prima_por_id

def mostrar_ventana_ventas():
    ventana = tk.Toplevel()
    ventana.title("Registrar Venta (Ticket)")
    ventana.geometry("700x850")  # Aumenta el tamaño para acomodar la información de stock

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

    # Etiqueta para mostrar la disponibilidad de stock
    label_stock_disponible = tk.Label(ventana, text="Stock de Materias Primas: ", font=("Helvetica", 10), fg="gray",
                                      justify=tk.LEFT)
    label_stock_disponible.pack(pady=(5, 0), padx=10, anchor="w")

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

    def calcular_disponibilidad_producto(producto_id):
        receta = obtener_receta_por_producto_id(producto_id)
        if not receta or not receta.ingredientes:
            return float('inf')
        min_unidades = float('inf')
        for ingrediente in receta.ingredientes:
            mp_id = ingrediente["materia_prima_id"]
            cantidad_necesaria = ingrediente["cantidad_necesaria"]
            materia_prima = obtener_materia_prima_por_id(mp_id)
            if not materia_prima:
                return 0
            if cantidad_necesaria > 0:
                unidades_posibles = materia_prima.stock / cantidad_necesaria
                min_unidades = min(min_unidades, unidades_posibles)
        return int(min_unidades) if min_unidades != float('inf') else float('inf')

    def cargar_productos_disponibles(filtro=""):
        lista_productos.delete(0, tk.END)
        filtro = filtro.lower()
        productos_filtrados = []
        global productos_disponibles
        productos_disponibles = listar_productos()
        for p in productos_disponibles:
            if filtro in p.nombre.lower():
                productos_filtrados.append(p)
        if not productos_filtrados:
            lista_productos.insert(tk.END, "No se encontraron productos.")
        else:
            for p in productos_filtrados:
                disponibilidad = calcular_disponibilidad_producto(p.id)
                stock_info = ""
                if disponibilidad == float('inf'):
                    stock_info = "(Stock ilimitado)"
                elif disponibilidad > 0:
                    stock_info = f"(Stock: {disponibilidad} unidades)"
                else:
                    stock_info = "(SIN STOCK)"
                precio_formateado = f"{p.precio_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista_productos.insert(tk.END, f"ID: {p.id[:8]}... - {p.nombre} - Gs {precio_formateado} {stock_info}")
        if lista_productos.size() > 0:
            lista_productos.selection_set(0)
            on_producto_seleccionado(None)

    def on_buscar(event):
        cargar_productos_disponibles(entry_buscar.get())

    def on_producto_seleccionado(event):
        try:
            seleccion_indices = lista_productos.curselection()
            if not seleccion_indices:
                label_stock_disponible.config(text="Stock de Materias Primas: ")
                return
            linea_seleccionada = lista_productos.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')
            producto_encontrado = None
            for p in productos_disponibles:
                if p.id.startswith(id_abrev):
                    producto_encontrado = p
                    break
            if not producto_encontrado:
                label_stock_disponible.config(text="Stock de Materias Primas: Error al cargar.")
                return
            receta = obtener_receta_por_producto_id(producto_encontrado.id)
            if not receta or not receta.ingredientes:
                label_stock_disponible.config(
                    text=f"Stock de Materias Primas para '{producto_encontrado.nombre}': No tiene receta o no consume MP.")
                return
            stock_info_text = f"Stock de Materias Primas para '{producto_encontrado.nombre}':\n"
            for ingrediente in receta.ingredientes:
                mp = obtener_materia_prima_por_id(ingrediente["materia_prima_id"])
                if mp:
                    stock_info_text += f"  - {mp.nombre}: {mp.stock} {mp.unidad_medida} (Necesario por unidad: {ingrediente['cantidad_necesaria']} {mp.unidad_medida})\n"
                else:
                    stock_info_text += f"  - {ingrediente['nombre_materia_prima']}: Materia prima no encontrada.\n"
            label_stock_disponible.config(text=stock_info_text)
        except Exception as e:
            label_stock_disponible.config(text=f"Stock de Materias Primas: Error ({e})")

    def actualizar_total_ticket():
        total = sum(item.total for item in venta_actual_items)
        label_total.config(text=f"Total: Gs {total:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def agregar_producto_a_venta():
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
            disponibilidad = calcular_disponibilidad_producto(producto_encontrado.id)
            if cantidad > disponibilidad:
                messagebox.showwarning("Stock Insuficiente",
                                       f"No hay suficiente stock de materias primas para producir {cantidad} unidades de '{producto_encontrado.nombre}'. Solo se pueden producir {disponibilidad} unidades.")
                return
            detalle_venta = VentaDetalle(
                producto_id=producto_encontrado.id,
                nombre_producto=producto_encontrado.nombre,
                cantidad=cantidad,
                precio_unitario=producto_encontrado.precio_unitario
            )
            venta_actual_items.append(detalle_venta)
            lista_venta.insert(tk.END,
                               f"{detalle_venta.nombre_producto} x {detalle_venta.cantidad} = Gs {detalle_venta.total:,.0f}".replace(
                                   ",", "X").replace(".", ",").replace("X", "."))
            actualizar_total_ticket()
            entry_cantidad.delete(0, tk.END)
            entry_cantidad.focus_set()
            cargar_productos_disponibles(entry_buscar.get())
            on_producto_seleccionado(None)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar producto al ticket: {e}")

    def generar_factura():
        cliente = entry_cliente.get().strip()
        if not cliente:
            messagebox.showwarning("Atención", "Por favor, ingrese el nombre del cliente.")
            return
        if not venta_actual_items:
            messagebox.showwarning("Atención", "No hay productos en la venta actual.")
            return
        confirmar_factura = messagebox.askyesno(
            "Confirmar Factura",
            f"¿Desea generar la factura para '{cliente}' con un total de Gs {sum(item.total for item in venta_actual_items):,.0f}?".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        if not confirmar_factura:
            messagebox.showinfo("Cancelado", "Generación de factura cancelada.")
            return
        try:
            ticket_generado = registrar_ticket(cliente, venta_actual_items)
            messagebox.showinfo("Factura Generada",
                                f"Factura generada con éxito para {cliente}.\nTotal: Gs {ticket_generado.total:,.0f}\nID Ticket: {ticket_generado.id[:8]}...".replace(",", "X").replace(".", ",").replace("X", "."))
            venta_actual_items.clear()
            lista_venta.delete(0, tk.END)
            label_total.config(text="Total: Gs 0")
            entry_cliente.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_cliente.focus_set()
            cargar_productos_disponibles()
            label_stock_disponible.config(text="Stock de Materias Primas: ")
        except ValueError as e:
            messagebox.showerror("Error al Generar Factura", str(e))
        except Exception as e:
            messagebox.showerror("Error al Generar Factura", f"No se pudo generar la factura.\nDetalle: {str(e)}")

    entry_buscar.bind("<KeyRelease>", on_buscar)
    lista_productos.bind("<<ListboxSelect>>", on_producto_seleccionado)

    tk.Button(ventana, text="Agregar Producto a Venta", command=agregar_producto_a_venta, width=25).pack(pady=5)
    tk.Button(ventana, text="Generar Factura", command=generar_factura, width=25, bg="lightgreen", fg="black").pack(
        pady=10)

    cargar_productos_disponibles()