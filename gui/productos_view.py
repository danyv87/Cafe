import tkinter as tk
from tkinter import messagebox, ttk
from controllers.pricing_controller import (
    PlanVentaItem,
    calcular_precio_sugerido,
    calcular_precio_sugerido_proporcional,
)
from controllers.productos_controller import (
    listar_productos,
    agregar_producto,
    validar_producto,
    editar_producto,
    eliminar_producto,
    actualizar_disponibilidad_productos,
    obtener_producto_por_id,
)
from controllers.planes_venta_controller import (
    cargar_planes_venta,
    guardar_plan_venta,
    eliminar_plan_venta,
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

    disponible_var_agregar = tk.BooleanVar(value=True)
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

    disponible_var_editar = tk.BooleanVar(value=True)
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
                disponible_var_agregar.set(True)
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
                disponible_var_editar.set(True)
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
                disponible_var_editar.set(True)

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar el producto: {e}")
            producto_seleccionado_id.set("")
            entry_nombre_editar.delete(0, tk.END)
            entry_precio_editar.delete(0, tk.END)
            disponible_var_editar.set(True)

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

    def abrir_plan_venta_multiple():
        """
        Abre una ventana para definir el menú de venta y calcular precios con estrategia multi-producto.
        """
        ventana_plan = tk.Toplevel(ventana)
        ventana_plan.title("Plan de Venta Multi-Producto")
        ventana_plan.geometry("820x720")
        ventana_plan.resizable(True, True)

        productos = listar_productos()
        productos.sort(key=lambda item: item.nombre.lower())
        plan_items = {}
        resultados_calculo = {}

        tk.Label(
            ventana_plan,
            text="Seleccione los productos del menú y defina unidades previstas/precios base.",
            font=("Helvetica", 10, "italic"),
            fg="gray",
            wraplength=760,
        ).pack(pady=(10, 5))

        frame_planes = tk.LabelFrame(ventana_plan, text="Planes guardados", padx=10, pady=10)
        frame_planes.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_planes, text="Nombre del plan:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        plan_nombre_var = tk.StringVar()
        combo_planes = ttk.Combobox(frame_planes, textvariable=plan_nombre_var, width=35)
        combo_planes.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        def refrescar_planes():
            planes = cargar_planes_venta()
            nombres = [plan.get("nombre") for plan in planes if plan.get("nombre")]
            combo_planes["values"] = nombres
            if nombres and not plan_nombre_var.get():
                plan_nombre_var.set(nombres[-1])
                cargar_plan_seleccionado()

        def cargar_plan_seleccionado():
            nombre = plan_nombre_var.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "Seleccione un plan para cargar.")
                return
            planes = cargar_planes_venta()
            plan = next((p for p in planes if p.get("nombre") == nombre), None)
            if not plan:
                messagebox.showerror("Error", "No se encontró el plan seleccionado.")
                return
            plan_items.clear()
            resultados_calculo.clear()
            lista_resultados.delete(0, tk.END)
            for item in plan.get("items", []):
                plan_items[item["id"]] = {
                    "id": item["id"],
                    "nombre": item["nombre"],
                    "unidades": item["unidades"],
                    "precio": item["precio"],
                }
            refrescar_plan()
            text_conclusion.config(state=tk.NORMAL)
            text_conclusion.delete("1.0", tk.END)
            text_conclusion.insert(
                tk.END,
                "Plan cargado. Calcule los precios sugeridos para ver la conclusión.",
            )
            text_conclusion.config(state=tk.DISABLED)

        def guardar_plan_actual():
            nombre = plan_nombre_var.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "Ingrese un nombre para guardar el plan.")
                return
            if not plan_items:
                messagebox.showwarning("Atención", "Agregue productos al plan antes de guardar.")
                return
            try:
                guardar_plan_venta(nombre, list(plan_items.values()))
            except ValueError as exc:
                messagebox.showerror("Error", str(exc))
                return
            refrescar_planes()
            messagebox.showinfo("Éxito", "Plan guardado correctamente.")

        def eliminar_plan_actual():
            nombre = plan_nombre_var.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "Seleccione un plan para eliminar.")
                return
            confirmar = messagebox.askyesno(
                "Confirmar Eliminación",
                "¿Está seguro de que desea eliminar este plan? Esta acción no se puede deshacer.",
            )
            if not confirmar:
                return
            try:
                eliminar_plan_venta(nombre)
            except ValueError as exc:
                messagebox.showerror("Error", str(exc))
                return
            plan_nombre_var.set("")
            plan_items.clear()
            refrescar_plan()
            refrescar_planes()
            text_conclusion.config(state=tk.NORMAL)
            text_conclusion.delete("1.0", tk.END)
            text_conclusion.insert(tk.END, "Plan eliminado. Cree o cargue otro plan.")
            text_conclusion.config(state=tk.DISABLED)

        tk.Button(frame_planes, text="Cargar", command=cargar_plan_seleccionado, width=12).grid(
            row=0, column=2, padx=5, pady=2
        )
        tk.Button(frame_planes, text="Guardar", command=guardar_plan_actual, width=12).grid(
            row=0, column=3, padx=5, pady=2
        )
        tk.Button(frame_planes, text="Eliminar", command=eliminar_plan_actual, width=12).grid(
            row=0, column=4, padx=5, pady=2
        )

        frame_productos = tk.LabelFrame(ventana_plan, text="Productos disponibles", padx=10, pady=10)
        frame_productos.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_productos, text="Buscar:", font=("Helvetica", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=5
        )
        entry_buscar = tk.Entry(frame_productos, width=30)
        entry_buscar.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        frame_lista_productos = tk.Frame(frame_productos)
        frame_lista_productos.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        frame_lista_productos.columnconfigure(0, weight=1)

        scrollbar_plan = tk.Scrollbar(frame_lista_productos, orient=tk.VERTICAL)
        lista_productos = tk.Listbox(
            frame_lista_productos,
            width=70,
            height=6,
            yscrollcommand=scrollbar_plan.set,
            exportselection=False,
            selectmode=tk.EXTENDED,
        )
        scrollbar_plan.config(command=lista_productos.yview)
        lista_productos.grid(row=0, column=0, sticky="nsew")
        scrollbar_plan.grid(row=0, column=1, sticky="ns")

        def cargar_lista_productos(filtro=""):
            lista_productos.delete(0, tk.END)
            filtro = filtro.lower().strip()
            for prod in productos:
                if filtro and filtro not in prod.nombre.lower():
                    continue
                precio = f"{prod.precio_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista_productos.insert(tk.END, f"ID: {prod.id[:8]}... - {prod.nombre} - Gs {precio}")

        def buscar_productos(event=None):
            cargar_lista_productos(entry_buscar.get())

        entry_buscar.bind("<KeyRelease>", buscar_productos)

        frame_detalle = tk.LabelFrame(ventana_plan, text="Detalle del plan", padx=10, pady=10)
        frame_detalle.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_detalle, text="Unidades previstas (UP):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        entry_unidades = tk.Entry(frame_detalle, width=15)
        entry_unidades.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        tk.Label(frame_detalle, text="Precio base (Gs):").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        entry_precio_base = tk.Entry(frame_detalle, width=15)
        entry_precio_base.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        def obtener_producto_por_linea(linea):
            id_abrev = linea.split(' ')[1].replace('...', '')
            for prod in productos:
                if prod.id.startswith(id_abrev):
                    return prod
            return None

        def on_producto_seleccionado_plan(event=None):
            seleccion = lista_productos.curselection()
            if not seleccion:
                return
            producto = obtener_producto_por_linea(lista_productos.get(seleccion[0]))
            if producto:
                entry_precio_base.delete(0, tk.END)
                entry_precio_base.insert(0, f"{producto.precio_unitario:.0f}")

        lista_productos.bind("<<ListboxSelect>>", on_producto_seleccionado_plan)

        def refrescar_plan():
            lista_plan.delete(0, tk.END)
            for item in plan_items.values():
                id_corto = item["id"][:8]
                precio = f"{item['precio']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista_plan.insert(
                    tk.END,
                    f"ID: {id_corto}... | {item['nombre']} | UP: {item['unidades']:.0f} | "
                    f"Precio base: Gs {precio}",
                )

        def agregar_al_plan():
            seleccion = lista_productos.curselection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione al menos un producto para agregar al plan.")
                return

            try:
                unidades = float(entry_unidades.get())
                precio_base = float(entry_precio_base.get())
            except ValueError:
                messagebox.showerror("Error de Entrada", "Ingrese unidades y precio base numéricos.")
                return

            if unidades <= 0 or precio_base < 0:
                messagebox.showerror(
                    "Error de Validación",
                    "Las unidades previstas deben ser mayores a cero y el precio base no puede ser negativo.",
                )
                return

            for indice in seleccion:
                producto = obtener_producto_por_linea(lista_productos.get(indice))
                if not producto:
                    continue
                plan_items[producto.id] = {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "unidades": unidades,
                    "precio": precio_base,
                }

            refrescar_plan()
            resultados_calculo.clear()
            lista_resultados.delete(0, tk.END)
            text_conclusion.config(state=tk.NORMAL)
            text_conclusion.delete("1.0", tk.END)
            text_conclusion.insert(
                tk.END,
                "Plan actualizado. Calcule los precios sugeridos para ver la conclusión.",
            )
            text_conclusion.config(state=tk.DISABLED)

        def quitar_del_plan():
            seleccion = lista_plan.curselection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione un ítem del plan para quitar.")
                return
            for indice in reversed(seleccion):
                linea = lista_plan.get(indice)
                id_abrev = linea.split(' ')[1].replace('...', '')
                producto_id = next(
                    (pid for pid in plan_items if pid.startswith(id_abrev)), None
                )
                if producto_id:
                    plan_items.pop(producto_id, None)
            refrescar_plan()
            resultados_calculo.clear()
            lista_resultados.delete(0, tk.END)
            text_conclusion.config(state=tk.NORMAL)
            text_conclusion.delete("1.0", tk.END)
            text_conclusion.insert(
                tk.END,
                "Plan actualizado. Calcule los precios sugeridos para ver la conclusión.",
            )
            text_conclusion.config(state=tk.DISABLED)

        tk.Button(frame_detalle, text="Agregar/Actualizar en plan", command=agregar_al_plan).grid(
            row=1, column=0, columnspan=2, pady=5
        )
        tk.Button(frame_detalle, text="Quitar del plan", command=quitar_del_plan).grid(
            row=1, column=2, columnspan=2, pady=5
        )

        frame_plan = tk.LabelFrame(ventana_plan, text="Productos en el plan de venta", padx=10, pady=10)
        frame_plan.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        lista_plan = tk.Listbox(frame_plan, width=80, height=6)
        lista_plan.pack(fill=tk.BOTH, expand=True)

        frame_costos = tk.LabelFrame(ventana_plan, text="Parámetros de cálculo", padx=10, pady=10)
        frame_costos.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_costos, text="Costos fijos del período (Gs):").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        entry_costos_fijos = tk.Entry(frame_costos, width=20)
        entry_costos_fijos.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_costos, text="Margen de utilidad (ej. 0.3):").grid(
            row=0, column=2, sticky="w", padx=5, pady=2
        )
        entry_margen = tk.Entry(frame_costos, width=15)
        entry_margen.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame_costos, text="IVA (ej. 0.10):").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        entry_iva = tk.Entry(frame_costos, width=15)
        entry_iva.insert(0, "0.10")
        entry_iva.grid(row=1, column=1, padx=5, pady=2)

        frame_resultados = tk.LabelFrame(ventana_plan, text="Resultados", padx=10, pady=10)
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        lista_resultados = tk.Listbox(frame_resultados, width=80, height=6)
        lista_resultados.pack(fill=tk.BOTH, expand=True)

        frame_conclusion = tk.LabelFrame(ventana_plan, text="Conclusión de la estrategia", padx=10, pady=10)
        frame_conclusion.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        text_conclusion = tk.Text(frame_conclusion, width=80, height=8, wrap=tk.WORD)
        text_conclusion.pack(fill=tk.BOTH, expand=True)
        text_conclusion.insert(
            tk.END,
            "Cree un plan o cargue uno existente para ver la conclusión de su estrategia.",
        )
        text_conclusion.config(state=tk.DISABLED)

        def calcular_precios_plan():
            if not plan_items:
                messagebox.showwarning("Atención", "Agregue productos al plan antes de calcular.")
                return
            try:
                costos_fijos = float(entry_costos_fijos.get())
                margen = float(entry_margen.get())
                iva = float(entry_iva.get())
            except ValueError:
                messagebox.showerror("Error de Entrada", "Los parámetros de cálculo deben ser numéricos.")
                return

            plan_ventas = [
                PlanVentaItem(
                    producto_id=producto_id,
                    unidades_previstas=item["unidades"],
                    precio_venta_unitario=item["precio"],
                )
                for producto_id, item in plan_items.items()
            ]

            lista_resultados.delete(0, tk.END)
            resultados_calculo.clear()
            text_conclusion.config(state=tk.NORMAL)
            text_conclusion.delete("1.0", tk.END)

            for producto_id, item in plan_items.items():
                try:
                    resultado = calcular_precio_sugerido_proporcional(
                        producto_id=producto_id,
                        costos_fijos_periodo=costos_fijos,
                        plan_ventas=plan_ventas,
                        margen_utilidad=margen,
                        iva=iva,
                    )
                except ValueError as exc:
                    messagebox.showerror("Error de Cálculo", str(exc))
                    return

                precio_con = f"{resultado.precio_venta_con_iva:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                precio_sin = f"{resultado.precio_venta_sin_impuestos:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista_resultados.insert(
                    tk.END,
                    f"{item['nombre']} | Precio sugerido (sin IVA): Gs {precio_sin} | con IVA: Gs {precio_con}",
                )
                resultados_calculo[producto_id] = resultado

            total_units = sum(item["unidades"] for item in plan_items.values())
            total_base = sum(item["unidades"] * item["precio"] for item in plan_items.values())
            total_sin_iva = sum(
                item["unidades"] * resultados_calculo[pid].precio_venta_sin_impuestos
                for pid, item in plan_items.items()
            )
            total_con_iva = sum(
                item["unidades"] * resultados_calculo[pid].precio_venta_con_iva
                for pid, item in plan_items.items()
            )
            promedio_con_iva = total_con_iva / total_units if total_units else 0

            def formatear_gs(valor):
                return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

            text_conclusion.insert(
                tk.END,
                "Resumen del plan de venta:\n"
                f"- Productos en el menú: {len(plan_items)}\n"
                f"- Unidades previstas totales: {total_units:.0f}\n"
                f"- Ventas base estimadas (sin estrategia): Gs {formatear_gs(total_base)}\n"
                f"- Ventas sugeridas sin IVA: Gs {formatear_gs(total_sin_iva)}\n"
                f"- Ventas sugeridas con IVA: Gs {formatear_gs(total_con_iva)}\n"
                f"- Precio promedio sugerido con IVA: Gs {formatear_gs(promedio_con_iva)}\n\n"
                "Distribución de ventas sugeridas por producto:\n"
            )

            for producto_id, item in plan_items.items():
                total_prod = item["unidades"] * resultados_calculo[producto_id].precio_venta_con_iva
                peso = (total_prod / total_con_iva * 100) if total_con_iva else 0
                text_conclusion.insert(
                    tk.END,
                    f"• {item['nombre']}: Gs {formatear_gs(total_prod)} ({peso:.1f}% del total)\n",
                )

            text_conclusion.config(state=tk.DISABLED)

        def aplicar_precios_plan():
            if not resultados_calculo:
                messagebox.showwarning(
                    "Atención", "Calcule los precios sugeridos antes de aplicar."
                )
                return
            errores = []
            for producto_id, resultado in resultados_calculo.items():
                producto = obtener_producto_por_id(producto_id)
                if not producto:
                    errores.append(producto_id)
                    continue
                try:
                    editar_producto(
                        producto_id,
                        producto.nombre,
                        resultado.precio_venta_con_iva,
                        disponible_venta=producto.disponible_venta,
                    )
                except ValueError:
                    errores.append(producto_id)

            cargar_productos()
            if errores:
                messagebox.showwarning(
                    "Atención",
                    "Algunos productos no pudieron actualizarse. Revise el listado.",
                )
            else:
                messagebox.showinfo("Éxito", "Precios sugeridos aplicados al menú de venta.")

        frame_botones = tk.Frame(ventana_plan)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Calcular precios sugeridos", command=calcular_precios_plan, width=25).grid(
            row=0, column=0, padx=5
        )
        tk.Button(frame_botones, text="Aplicar precios al menú", command=aplicar_precios_plan, width=25).grid(
            row=0, column=1, padx=5
        )

        refrescar_planes()
        cargar_lista_productos()

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
    tk.Button(
        frame_form_editar,
        text="Plan de Venta Multi-Producto",
        command=abrir_plan_venta_multiple,
        width=42,
        bg="lightyellow",
    ).grid(row=7, column=0, columnspan=2, pady=5, padx=5)

    lista.bind("<<ListboxSelect>>", seleccionar_producto) # Vincula el evento de selección

    cargar_productos() # Carga los productos al abrir la ventana
