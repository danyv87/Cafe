import tkinter as tk
from tkinter import messagebox
from controllers.productos_controller import listar_productos, agregar_producto, validar_producto, editar_producto, eliminar_producto

def mostrar_ventana_productos():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Productos")
    ventana.geometry("600x650") # Ajusta el tamaño para acomodar los nuevos textos guía
    ventana.resizable(False, False) # Hacer la ventana no redimensionable

    # --- Variables para los campos de edición ---
    producto_seleccionado_id = tk.StringVar()

    # --- Widgets de la Interfaz ---

    # Título principal
    tk.Label(ventana, text="Gestión de Productos", font=("Helvetica", 16, "bold")).pack(pady=(15, 5))
    tk.Label(ventana, text="Aquí puede administrar los productos de su cafetería.", font=("Helvetica", 10, "italic"), fg="gray").pack(pady=(0, 10))


    # Frame para la lista de productos
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True, padx=10) # Añadir padx

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=70, height=10, yscrollcommand=scrollbar.set, exportselection=False) # Aumentar altura
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame para el formulario de Agregar
    frame_form_agregar = tk.LabelFrame(ventana, text="Agregar Nuevo Producto", padx=10, pady=10)
    frame_form_agregar.pack(pady=10, fill=tk.X, padx=10) # Añadir padx

    tk.Label(frame_form_agregar, text="Complete los campos para añadir un nuevo producto al sistema.", font=("Helvetica", 9, "italic"), fg="gray").grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

    tk.Label(frame_form_agregar, text="Nombre:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_nombre = tk.Entry(frame_form_agregar, width=40)
    entry_nombre.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form_agregar, text="Precio (Gs):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_precio = tk.Entry(frame_form_agregar, width=40)
    entry_precio.grid(row=2, column=1, padx=5, pady=2)

    # Frame para el formulario de Editar/Eliminar
    frame_form_editar = tk.LabelFrame(ventana, text="Editar / Eliminar Producto Seleccionado", padx=10, pady=10)
    frame_form_editar.pack(pady=10, fill=tk.X, padx=10) # Añadir padx

    tk.Label(frame_form_editar, text="Seleccione un producto de la lista superior para editar o eliminar.", font=("Helvetica", 9, "italic"), fg="gray").grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

    tk.Label(frame_form_editar, text="Nombre:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_nombre_editar = tk.Entry(frame_form_editar) # Ahora creado antes de las funciones que lo usan
    entry_nombre_editar.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form_editar, text="Precio (Gs):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_precio_editar = tk.Entry(frame_form_editar) # Ahora creado antes de las funciones que lo usan
    entry_precio_editar.grid(row=2, column=1, padx=5, pady=2)

    # --- Funciones (definidas DESPUÉS de los widgets que usan) ---

    def cargar_productos():
        """
        Carga los productos desde el controlador y los muestra en el Listbox.
        """
        lista.delete(0, tk.END)
        productos = listar_productos()
        # Ordenar alfabéticamente por nombre, ignorando mayúsculas/minúsculas
        productos.sort(key=lambda mp: mp.nombre.lower())
        if not productos:
            lista.insert(tk.END, "No hay productos registrados.")
        else:
            for p in productos:
                lista.insert(tk.END, f"ID: {p.id[:8]}... - {p.nombre} - Gs {p.precio_unitario:.0f}")

    def agregar():
        """
        Función para agregar un nuevo producto.
        Incluye validación y confirmación.
        """
        nombre = entry_nombre.get()
        precio_str = entry_precio.get()

        try:
            precio = float(precio_str)
        except ValueError:
            messagebox.showerror("Error de Entrada", "El precio debe ser un número válido.")
            return

        es_valido, mensaje_error = validar_producto(nombre, precio)
        if not es_valido:
            messagebox.showerror("Error de Validación", mensaje_error)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Adición",
            f"¿Desea agregar el producto '{nombre}' con precio Gs {precio:.0f}?"
        )
        if confirmar:
            try:
                agregar_producto(nombre, precio)
                cargar_productos()
                entry_nombre.delete(0, tk.END)
                entry_precio.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Agregar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        else:
            messagebox.showinfo("Cancelado", "Adición de producto cancelada.")

    def seleccionar_producto(event):
        """
        Función que se ejecuta al seleccionar un producto en el Listbox.
        Carga los datos del producto seleccionado en los campos de edición.
        """
        try:
            seleccion_indices = lista.curselection()
            if not seleccion_indices:
                # Limpiar campos si no hay selección o la selección se desactiva
                producto_seleccionado_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_precio_editar.delete(0, tk.END)
                return

            linea_seleccionada = lista.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            productos_cargados = listar_productos()
            producto_encontrado = None
            for p in productos_cargados:
                if p.id.startswith(id_abrev):
                    producto_encontrado = p
                    break

            if producto_encontrado:
                producto_seleccionado_id.set(producto_encontrado.id)
                entry_nombre_editar.delete(0, tk.END)
                entry_nombre_editar.insert(0, producto_encontrado.nombre)
                entry_precio_editar.delete(0, tk.END)
                entry_precio_editar.insert(0, str(producto_encontrado.precio_unitario))
            else:
                messagebox.showwarning("Error", "No se pudo encontrar el producto completo.")
                producto_seleccionado_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_precio_editar.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar el producto: {e}")
            producto_seleccionado_id.set("")
            entry_nombre_editar.delete(0, tk.END)
            entry_precio_editar.delete(0, tk.END)

    def editar():
        """
        Función para editar un producto existente.
        """
        id_a_editar = producto_seleccionado_id.get()
        if not id_a_editar:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista para editar.")
            return

        nuevo_nombre = entry_nombre_editar.get()
        nuevo_precio_str = entry_precio_editar.get()

        try:
            nuevo_precio = float(nuevo_precio_str)
        except ValueError:
            messagebox.showerror("Error de Entrada", "El nuevo precio debe ser un número válido.")
            return

        es_valido, mensaje_error = validar_producto(nuevo_nombre, nuevo_precio)
        if not es_valido:
            messagebox.showerror("Error de Validación", mensaje_error)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Edición",
            f"¿Desea guardar los cambios para el producto '{nuevo_nombre}' con precio Gs {nuevo_precio:.0f}?"
        )
        if confirmar:
            try:
                editar_producto(id_a_editar, nuevo_nombre, nuevo_precio)
                cargar_productos()
                producto_seleccionado_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_precio_editar.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Producto editado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Editar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al editar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Edición de producto cancelada.")

    def eliminar():
        """
        Función para eliminar un producto.
        """
        id_a_eliminar = producto_seleccionado_id.get()
        if not id_a_eliminar:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista para eliminar.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este producto? Esta acción no se puede deshacer."
        )
        if confirmar:
            try:
                eliminar_producto(id_a_eliminar)
                cargar_productos()
                producto_seleccionado_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_precio_editar.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Eliminar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Eliminación de producto cancelada.")

    # --- Botones de acción ---
    tk.Button(frame_form_agregar, text="Agregar producto", command=agregar, width=20).grid(row=3, column=0, columnspan=2, pady=5)
    tk.Button(frame_form_editar, text="Editar Producto", command=editar, width=20, bg="lightblue").grid(row=3, column=0, pady=5, padx=5)
    tk.Button(frame_form_editar, text="Eliminar Producto", command=eliminar, width=20, bg="lightcoral").grid(row=3, column=1, pady=5, padx=5)

    lista.bind("<<ListboxSelect>>", seleccionar_producto) # Vincula el evento de selección

    cargar_productos() # Carga los productos al abrir la ventana
