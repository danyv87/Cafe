import tkinter as tk
from tkinter import messagebox
from controllers.pricing_controller import calcular_precio_sugerido
from controllers.productos_controller import (
    listar_productos,
    agregar_producto,
    validar_producto,
    editar_producto,
    eliminar_producto,
    actualizar_disponibilidad_productos,
)

def mostrar_ventana_productos():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Productos")
    ventana.geometry("700x900") # Ajusta el tamaño para acomodar los nuevos textos guía
    ventana.resizable(True, True) # Habilitar redimensionado para ver todas las secciones

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
    lista = tk.Listbox(
        frame_lista,
        width=70,
        height=10,
        yscrollcommand=scrollbar.set,
        exportselection=False,
        selectmode=tk.EXTENDED,
    ) # Aumentar altura
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

    tk.Label(frame_form_agregar, text="Precio (Gs) por unidad:").grid(
        row=2, column=0, padx=5, pady=2, sticky="w"
    )
    entry_precio = tk.Entry(frame_form_agregar, width=40)
    entry_precio.grid(row=2, column=1, padx=5, pady=2)
    tk.Label(
        frame_form_agregar,
        text="El precio se ingresa manualmente o puede calcularse en el editor.",
        font=("Helvetica", 8, "italic"),
        fg="gray",
    ).grid(row=3, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

    disponible_var_agregar = tk.BooleanVar(value=False)
    tk.Checkbutton(
        frame_form_agregar,
        text="Disponible para la venta",
        variable=disponible_var_agregar,
    ).grid(row=4, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

    # Frame para el formulario de Editar/Eliminar
    frame_form_editar = tk.LabelFrame(ventana, text="Editar / Eliminar Producto Seleccionado", padx=10, pady=10)
    frame_form_editar.pack(pady=10, fill=tk.X, padx=10) # Añadir padx

    tk.Label(frame_form_editar, text="Seleccione un producto de la lista superior para editar o eliminar.", font=("Helvetica", 9, "italic"), fg="gray").grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

    tk.Label(frame_form_editar, text="Nombre:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_nombre_editar = tk.Entry(frame_form_editar) # Ahora creado antes de las funciones que lo usan
    entry_nombre_editar.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form_editar, text="Precio (Gs) por unidad:").grid(
        row=2, column=0, padx=5, pady=2, sticky="w"
    )
    entry_precio_editar = tk.Entry(frame_form_editar) # Ahora creado antes de las funciones que lo usan
    entry_precio_editar.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(
        frame_form_editar,
        text="Puede calcular un precio sugerido con costos fijos, UP, margen e IVA.",
        font=("Helvetica", 8, "italic"),
        fg="gray",
    ).grid(row=3, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

    disponible_var_editar = tk.BooleanVar(value=False)
    tk.Checkbutton(
        frame_form_editar,
        text="Disponible para la venta",
        variable=disponible_var_editar,
    ).grid(row=4, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

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
                disponibilidad = "" if p.disponible_venta else " (No disponible)"
                lista.insert(
                    tk.END,
                    f"ID: {p.id[:8]}... - {p.nombre} - Gs {p.precio_unitario:.0f}{disponibilidad}",
                )

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
                agregar_producto(
                    nombre,
                    precio,
                    disponible_venta=disponible_var_agregar.get(),
                )
                cargar_productos()
                entry_nombre.delete(0, tk.END)
                entry_precio.delete(0, tk.END)
                disponible_var_agregar.set(False)
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
                disponible_var_editar.set(False)
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
                disponible_var_editar.set(producto_encontrado.disponible_venta)
            else:
                messagebox.showwarning("Error", "No se pudo encontrar el producto completo.")
                producto_seleccionado_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_precio_editar.delete(0, tk.END)
                disponible_var_editar.set(False)

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar el producto: {e}")
            producto_seleccionado_id.set("")
            entry_nombre_editar.delete(0, tk.END)
            entry_precio_editar.delete(0, tk.END)
            disponible_var_editar.set(False)

    def obtener_ids_seleccionados():
        seleccion_indices = lista.curselection()
        if not seleccion_indices:
            return []

        productos = listar_productos()
        ids = []
        for indice in seleccion_indices:
            linea_seleccionada = lista.get(indice)
            if "ID:" not in linea_seleccionada:
                continue
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')
            for producto in productos:
                if producto.id.startswith(id_abrev):
                    ids.append(producto.id)
                    break
        return ids

    def aplicar_disponibilidad(disponible):
        ids = obtener_ids_seleccionados()
        if not ids:
            messagebox.showwarning(
                "Atención",
                "Seleccione uno o más productos de la lista para actualizar disponibilidad.",
            )
            return
        actualizados = actualizar_disponibilidad_productos(ids, disponible)
        cargar_productos()
        messagebox.showinfo(
            "Disponibilidad actualizada",
            f"Se actualizaron {actualizados} productos.",
        )

    def marcar_todos(disponible):
        productos = listar_productos()
        if not productos:
            messagebox.showwarning("Atención", "No hay productos registrados.")
            return
        ids = [p.id for p in productos]
        actualizar_disponibilidad_productos(ids, disponible)
        cargar_productos()
        messagebox.showinfo(
            "Disponibilidad actualizada",
            "Se actualizó la disponibilidad de todos los productos.",
        )

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
                editar_producto(
                    id_a_editar,
                    nuevo_nombre,
                    nuevo_precio,
                    disponible_venta=disponible_var_editar.get(),
                )
                cargar_productos()
                producto_seleccionado_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_precio_editar.delete(0, tk.END)
                disponible_var_editar.set(True)
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

    def abrir_calculadora_precio():
        """
        Abre una ventana para calcular el precio sugerido usando CV, CF/UP, MU e IVA.
        """
        producto_id = producto_seleccionado_id.get()
        if not producto_id:
            messagebox.showwarning("Atención", "Seleccione un producto para calcular su precio.")
            return

        ventana_calculo = tk.Toplevel(ventana)
        ventana_calculo.title("Calculadora de Precio Sugerido")
        ventana_calculo.geometry("480x420")
        ventana_calculo.resizable(False, False)

        tk.Label(
            ventana_calculo,
            text="Ingrese los costos fijos, UP, margen e IVA para calcular el precio sugerido.",
            font=("Helvetica", 9, "italic"),
            fg="gray",
            wraplength=440,
        ).pack(pady=(10, 5))

        frame_inputs = tk.Frame(ventana_calculo)
        frame_inputs.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(frame_inputs, text="Costos fijos del período (Gs):").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        entry_costos_fijos = tk.Entry(frame_inputs, width=20)
        entry_costos_fijos.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="UP (unidades previstas):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        entry_up = tk.Entry(frame_inputs, width=20)
        entry_up.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="Margen de utilidad (ej. 0.3):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        entry_margen = tk.Entry(frame_inputs, width=20)
        entry_margen.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="IVA (ej. 0.10):").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        entry_iva = tk.Entry(frame_inputs, width=20)
        entry_iva.insert(0, "0.10")
        entry_iva.grid(row=3, column=1, padx=5, pady=5)

        frame_resultados = tk.LabelFrame(ventana_calculo, text="Resultados", padx=10, pady=10)
        frame_resultados.pack(padx=10, pady=10, fill=tk.X)

        resultado_labels = {
            "cv": tk.Label(frame_resultados, text="Costo variable unitario: -"),
            "cf": tk.Label(frame_resultados, text="Costo fijo unitario: -"),
            "ct": tk.Label(frame_resultados, text="Costo total unitario: -"),
            "pv_sin": tk.Label(frame_resultados, text="Precio sin impuestos: -"),
            "pv_con": tk.Label(frame_resultados, text="Precio con IVA: -"),
        }

        for idx, label in enumerate(resultado_labels.values()):
            label.grid(row=idx, column=0, sticky="w", pady=2)

        resultado_precio = {"valor": None}

        def formatear_gs(valor):
            return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def calcular():
            try:
                costos_fijos = float(entry_costos_fijos.get())
                unidades_previstas = float(entry_up.get())
                margen = float(entry_margen.get())
                iva = float(entry_iva.get())
            except ValueError:
                messagebox.showerror("Error de Entrada", "Todos los valores deben ser numéricos.")
                return

            try:
                resultado = calcular_precio_sugerido(
                    producto_id=producto_id,
                    costos_fijos_periodo=costos_fijos,
                    unidades_previstas=unidades_previstas,
                    margen_utilidad=margen,
                    iva=iva,
                )
            except ValueError as exc:
                messagebox.showerror("Error de Cálculo", str(exc))
                return

            resultado_labels["cv"].config(
                text=f"Costo variable unitario: Gs {formatear_gs(resultado.costo_variable_unitario)}"
            )
            resultado_labels["cf"].config(
                text=f"Costo fijo unitario: Gs {formatear_gs(resultado.costo_fijo_unitario)}"
            )
            resultado_labels["ct"].config(
                text=f"Costo total unitario: Gs {formatear_gs(resultado.costo_total_unitario)}"
            )
            resultado_labels["pv_sin"].config(
                text=f"Precio sin impuestos: Gs {formatear_gs(resultado.precio_venta_sin_impuestos)}"
            )
            resultado_labels["pv_con"].config(
                text=f"Precio con IVA: Gs {formatear_gs(resultado.precio_venta_con_iva)}"
            )
            resultado_precio["valor"] = resultado.precio_venta_con_iva

        def aplicar_precio():
            if resultado_precio["valor"] is None:
                messagebox.showwarning(
                    "Atención", "Primero calcule el precio sugerido antes de aplicar."
                )
                return
            entry_precio_editar.delete(0, tk.END)
            entry_precio_editar.insert(0, f"{resultado_precio['valor']:.0f}")
            messagebox.showinfo(
                "Precio aplicado", "El precio con IVA fue aplicado al campo de edición."
            )

        frame_botones = tk.Frame(ventana_calculo)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Calcular", command=calcular, width=15).grid(
            row=0, column=0, padx=5
        )
        tk.Button(frame_botones, text="Aplicar precio", command=aplicar_precio, width=15).grid(
            row=0, column=1, padx=5
        )

    # --- Botones de acción ---
    tk.Button(frame_form_agregar, text="Agregar producto", command=agregar, width=20).grid(
        row=5, column=0, columnspan=2, pady=5
    )
    tk.Button(frame_form_editar, text="Editar Producto", command=editar, width=20, bg="lightblue").grid(
        row=5, column=0, pady=5, padx=5
    )
    tk.Button(frame_form_editar, text="Eliminar Producto", command=eliminar, width=20, bg="lightcoral").grid(
        row=5, column=1, pady=5, padx=5
    )
    tk.Button(
        frame_form_editar,
        text="Calcular Precio Sugerido",
        command=abrir_calculadora_precio,
        width=42,
        bg="lightgreen",
    ).grid(row=6, column=0, columnspan=2, pady=5, padx=5)

    frame_disponibilidad = tk.LabelFrame(
        ventana,
        text="Editar disponibilidad en lote",
        padx=10,
        pady=10,
    )
    frame_disponibilidad.pack(pady=5, fill=tk.X, padx=10)

    tk.Label(
        frame_disponibilidad,
        text="Seleccione uno o más productos en la lista y use los botones.",
        font=("Helvetica", 9, "italic"),
        fg="gray",
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

    tk.Button(
        frame_disponibilidad,
        text="Marcar seleccionados como disponibles",
        command=lambda: aplicar_disponibilidad(True),
        width=34,
    ).grid(row=1, column=0, padx=5, pady=2, sticky="w")

    tk.Button(
        frame_disponibilidad,
        text="Marcar seleccionados como no disponibles",
        command=lambda: aplicar_disponibilidad(False),
        width=34,
    ).grid(row=1, column=1, padx=5, pady=2, sticky="w")

    tk.Button(
        frame_disponibilidad,
        text="Marcar todos como disponibles",
        command=lambda: marcar_todos(True),
        width=34,
    ).grid(row=2, column=0, padx=5, pady=2, sticky="w")

    tk.Button(
        frame_disponibilidad,
        text="Marcar todos como no disponibles",
        command=lambda: marcar_todos(False),
        width=34,
    ).grid(row=2, column=1, padx=5, pady=2, sticky="w")

    lista.bind("<<ListboxSelect>>", seleccionar_producto) # Vincula el evento de selección

    cargar_productos() # Carga los productos al abrir la ventana
