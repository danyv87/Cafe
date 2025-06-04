import tkinter as tk
from tkinter import messagebox, ttk  # Importar ttk para Combobox y Treeview
from controllers.recetas_controller import (
    listar_recetas,
    agregar_receta,
    editar_receta,
    eliminar_receta,
    obtener_receta_por_producto_id,
    validar_ingredientes_receta
)
from controllers.productos_controller import listar_productos, obtener_producto_por_id
from controllers.materia_prima_controller import listar_materias_primas, obtener_materia_prima_por_id


def mostrar_ventana_recetas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Recetas")
    ventana.geometry("800x750")  # Tamaño aumentado para más elementos

    # --- Variables para los campos de entrada y selección ---
    producto_seleccionado_var = tk.StringVar()
    materia_prima_seleccionada_var = tk.StringVar()
    cantidad_necesaria_var = tk.StringVar()

    # Variable para almacenar los ingredientes temporales de la receta que se está creando/editando
    ingredientes_receta_actual = []
    # Variable para almacenar el ID de la receta seleccionada para edición/eliminación
    receta_seleccionada_id = tk.StringVar()

    # --- Widgets de la Interfaz ---

    # Frame para la lista de recetas existentes
    frame_lista_recetas = tk.LabelFrame(ventana, text="Recetas Existentes", padx=10, pady=10)
    frame_lista_recetas.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar_recetas = tk.Scrollbar(frame_lista_recetas, orient=tk.VERTICAL)
    lista_recetas = tk.Listbox(frame_lista_recetas, width=100, height=8, yscrollcommand=scrollbar_recetas.set,
                               exportselection=False)
    scrollbar_recetas.config(command=lista_recetas.yview)
    scrollbar_recetas.pack(side=tk.RIGHT, fill=tk.Y)
    lista_recetas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame para crear/editar receta
    frame_form_receta = tk.LabelFrame(ventana, text="Crear / Editar Receta", padx=10, pady=10)
    frame_form_receta.pack(pady=10, fill=tk.X)

    # Selección de Producto
    tk.Label(frame_form_receta, text="Producto:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    combobox_productos = ttk.Combobox(frame_form_receta, textvariable=producto_seleccionado_var, state="readonly",
                                      width=50)
    combobox_productos.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    # Frame para añadir ingredientes a la receta
    frame_ingredientes = tk.LabelFrame(frame_form_receta, text="Ingredientes de la Receta", padx=10, pady=10)
    frame_ingredientes.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

    tk.Label(frame_ingredientes, text="Materia Prima:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    combobox_materias_primas = ttk.Combobox(frame_ingredientes, textvariable=materia_prima_seleccionada_var,
                                            state="readonly", width=40)
    combobox_materias_primas.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    tk.Label(frame_ingredientes, text="Cantidad Necesaria:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
    entry_cantidad_necesaria = tk.Entry(frame_ingredientes, textvariable=cantidad_necesaria_var, width=15)
    entry_cantidad_necesaria.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

    btn_agregar_ingrediente = tk.Button(frame_ingredientes, text="Añadir Ingrediente",
                                        command=lambda: agregar_ingrediente_a_lista_temporal())
    btn_agregar_ingrediente.grid(row=0, column=4, padx=5, pady=2, sticky="ew")

    # Listbox para mostrar los ingredientes añadidos temporalmente
    tk.Label(frame_ingredientes, text="Ingredientes Añadidos:").grid(row=1, column=0, columnspan=5, padx=5, pady=5,
                                                                     sticky="w")

    scrollbar_ingredientes_temp = tk.Scrollbar(frame_ingredientes, orient=tk.VERTICAL)
    lista_ingredientes_temp = tk.Listbox(frame_ingredientes, width=80, height=5,
                                         yscrollcommand=scrollbar_ingredientes_temp.set)
    scrollbar_ingredientes_temp.config(command=lista_ingredientes_temp.yview)
    scrollbar_ingredientes_temp.grid(row=2, column=5, sticky="ns")
    lista_ingredientes_temp.grid(row=2, column=0, columnspan=5, padx=5, pady=2, sticky="ew")

    btn_quitar_ingrediente = tk.Button(frame_ingredientes, text="Quitar Ingrediente Seleccionado",
                                       command=lambda: quitar_ingrediente_de_lista_temporal())
    btn_quitar_ingrediente.grid(row=3, column=0, columnspan=5, pady=5, sticky="ew")

    # --- Funciones ---

    def cargar_productos_y_materias_primas():
        """
        Carga los productos y materias primas en los Comboboxes.
        """
        productos = listar_productos()
        print(f"DEBUG: Productos cargados para combobox: {[p.nombre for p in productos]}")  # DEBUG LINE
        if not productos:
            messagebox.showwarning("Advertencia", "No hay productos registrados. Por favor, agregue productos primero.")
            combobox_productos["values"] = ["No hay productos"]
            combobox_productos.set("No hay productos")
        else:
            # Almacenar el objeto Producto completo en el valor del combobox para fácil acceso
            combobox_productos["values"] = [p.nombre for p in productos]
            # Mapeo de nombre a objeto para obtener el ID fácilmente
            combobox_productos.productos_map = {p.nombre: p for p in productos}
            if productos:
                combobox_productos.set(productos[0].nombre)  # Seleccionar el primero por defecto

        materias_primas = listar_materias_primas()
        print(f"DEBUG: Materias primas cargadas para combobox: {[mp.nombre for mp in materias_primas]}")  # DEBUG LINE
        if not materias_primas:
            messagebox.showwarning("Advertencia",
                                   "No hay materias primas registradas. Por favor, agregue materias primas primero.")
            combobox_materias_primas["values"] = ["No hay materias primas"]
            combobox_materias_primas.set("No hay materias primas")
        else:
            # Almacenar el objeto MateriaPrima completo en el valor del combobox
            combobox_materias_primas["values"] = [mp.nombre for mp in materias_primas]
            # Mapeo de nombre a objeto para obtener el ID fácilmente
            combobox_materias_primas.materias_primas_map = {mp.nombre: mp for mp in materias_primas}
            if materias_primas:
                combobox_materias_primas.set(materias_primas[0].nombre)  # Seleccionar la primera por defecto

    def cargar_recetas_en_gui():
        """
        Carga las recetas desde el controlador y las muestra en el Listbox.
        """
        lista_recetas.delete(0, tk.END)
        recetas = listar_recetas()
        print(f"DEBUG: Recetas cargadas para GUI: {[r.producto_nombre for r in recetas]}")  # DEBUG LINE
        if not recetas:
            lista_recetas.insert(tk.END, "No hay recetas registradas.")
        else:
            for r in recetas:
                # Asegurarse de que r.producto_nombre no sea None
                producto_nombre_display = r.producto_nombre if r.producto_nombre else "Producto Desconocido"
                ingredientes_str = ", ".join([f"{item['cantidad_necesaria']} {obtener_materia_prima_por_id(item['materia_prima_id']).unidad_medida} de {obtener_materia_prima_por_id(item['materia_prima_id']).nombre}" for item in r.ingredientes])
                lista_recetas.insert(tk.END, f"ID: {r.id[:8]}... - Producto: {producto_nombre_display} - Ingredientes: [{ingredientes_str}]")

    def agregar_ingrediente_a_lista_temporal():
        """
        Añade un ingrediente a la lista temporal para la receta actual.
        """
        mp_nombre = materia_prima_seleccionada_var.get()
        cantidad_str = cantidad_necesaria_var.get()

        if not mp_nombre or mp_nombre == "No hay materias primas":
            messagebox.showwarning("Advertencia", "Seleccione una materia prima.")
            return

        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad necesaria debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad necesaria debe ser un número válido.")
            return

        # Obtener el objeto MateriaPrima completo del mapa
        materia_prima_obj = combobox_materias_primas.materias_primas_map.get(mp_nombre)
        if not materia_prima_obj:
            messagebox.showerror("Error", "Materia prima seleccionada no válida.")
            return

        # Verificar si el ingrediente ya fue añadido para este producto
        for item in ingredientes_receta_actual:
            if item['materia_prima_id'] == materia_prima_obj.id:
                messagebox.showwarning("Advertencia",
                                       f"La materia prima '{mp_nombre}' ya ha sido añadida a esta receta. Edite la cantidad si desea cambiarla.")
                return

        ingredientes_receta_actual.append({
            "materia_prima_id": materia_prima_obj.id,
            "cantidad_necesaria": cantidad,
            "nombre_materia_prima": materia_prima_obj.nombre,  # Añadir nombre para facilitar la visualización
            "unidad_medida": materia_prima_obj.unidad_medida  # Añadir unidad de medida
        })
        actualizar_lista_ingredientes_temp()
        cantidad_necesaria_var.set("")  # Limpiar campo de cantidad

    def quitar_ingrediente_de_lista_temporal():
        """
        Quita un ingrediente de la lista temporal.
        """
        try:
            seleccion_indices = lista_ingredientes_temp.curselection()
            if not seleccion_indices:
                messagebox.showwarning("Atención", "Seleccione un ingrediente para quitar.")
                return

            indice = seleccion_indices[0]
            del ingredientes_receta_actual[indice]
            actualizar_lista_ingredientes_temp()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al quitar ingrediente: {e}")

    def actualizar_lista_ingredientes_temp():
        """
        Actualiza el Listbox que muestra los ingredientes temporales.
        """
        lista_ingredientes_temp.delete(0, tk.END)
        if not ingredientes_receta_actual:
            lista_ingredientes_temp.insert(tk.END, "No hay ingredientes añadidos para esta receta.")
        else:
            for item in ingredientes_receta_actual:
                lista_ingredientes_temp.insert(tk.END, f"{item['cantidad_necesaria']} {item['unidad_medida']} de {item['nombre_materia_prima']}")

    def guardar_receta():
        """
        Guarda la receta actual (nueva o editada).
        """
        producto_nombre = producto_seleccionado_var.get()
        if not producto_nombre or producto_nombre == "No hay productos":
            messagebox.showwarning("Advertencia", "Seleccione un producto para la receta.")
            return

        if not ingredientes_receta_actual:
            messagebox.showwarning("Advertencia", "Una receta debe tener al menos un ingrediente.")
            return

        # Obtener el ID completo del producto
        producto_obj = combobox_productos.productos_map.get(producto_nombre)
        if not producto_obj:
            messagebox.showerror("Error", "Producto seleccionado no válido.")
            return

        producto_id = producto_obj.id

        # Validar los ingredientes con el controlador
        es_valido, mensaje_error = validar_ingredientes_receta(ingredientes_receta_actual)
        if not es_valido:
            messagebox.showerror("Error de Validación", mensaje_error)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Receta",
            f"¿Desea guardar la receta para el producto '{producto_nombre}'?"
        )
        if confirmar:
            try:
                if receta_seleccionada_id.get():  # Si hay un ID de receta seleccionado, es una edición
                    editar_receta(receta_seleccionada_id.get(), ingredientes_receta_actual)
                    messagebox.showinfo("Éxito", "Receta editada correctamente.")
                else:  # Si no hay ID, es una nueva receta
                    agregar_receta(producto_id, producto_nombre, ingredientes_receta_actual)
                    messagebox.showinfo("Éxito", "Receta agregada correctamente.")

                limpiar_campos_receta()
                cargar_recetas_en_gui()
            except ValueError as e:
                messagebox.showerror("Error al Guardar Receta", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al guardar la receta: {e}")
        else:
            messagebox.showinfo("Cancelado", "Operación de receta cancelada.")

    def seleccionar_receta(event):
        """
        Función que se ejecuta al seleccionar una receta en el Listbox.
        Carga los datos de la receta seleccionada para edición.
        """
        try:
            seleccion_indices = lista_recetas.curselection()
            if not seleccion_indices:
                return

            linea_seleccionada = lista_recetas.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            recetas_cargadas = listar_recetas()
            receta_encontrada = None
            for r in recetas_cargadas:
                if r.id.startswith(id_abrev):
                    receta_encontrada = r
                    break

            if receta_encontrada:
                receta_seleccionada_id.set(receta_encontrada.id)
                producto_seleccionado_var.set(receta_encontrada.producto_nombre)

                ingredientes_receta_actual.clear()
                for item in receta_encontrada.ingredientes:
                    # Necesitamos el nombre y unidad de medida de la materia prima para mostrar
                    mp_obj = obtener_materia_prima_por_id(item['materia_prima_id'])
                    if mp_obj:
                        ingredientes_receta_actual.append({
                            "materia_prima_id": item['materia_prima_id'],
                            "cantidad_necesaria": item['cantidad_necesaria'],
                            "nombre_materia_prima": mp_obj.nombre,
                            "unidad_medida": mp_obj.unidad_medida
                        })
                actualizar_lista_ingredientes_temp()
            else:
                messagebox.showwarning("Error", "No se pudo encontrar la receta completa.")
                limpiar_campos_receta()

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar la receta: {e}")
            limpiar_campos_receta()

    def eliminar_receta_seleccionada():
        """
        Elimina la receta seleccionada.
        """
        id_a_eliminar = receta_seleccionada_id.get()
        if not id_a_eliminar:
            messagebox.showwarning("Atención", "Seleccione una receta de la lista para eliminar.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar esta receta? Esta acción no se puede deshacer."
        )
        if confirmar:
            try:
                eliminar_receta(id_a_eliminar)
                cargar_recetas_en_gui()
                limpiar_campos_receta()
                messagebox.showinfo("Éxito", "Receta eliminada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Eliminar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Eliminación de receta cancelada.")

    def limpiar_campos_receta():
        """
        Limpia todos los campos de entrada y la lista de ingredientes temporales.
        """
        producto_seleccionado_var.set("")
        materia_prima_seleccionada_var.set("")
        cantidad_necesaria_var.set("")
        ingredientes_receta_actual.clear()
        lista_ingredientes_temp.delete(0, tk.END)
        receta_seleccionada_id.set("")
        # Re-seleccionar el primer producto/materia prima si existen
        if combobox_productos["values"] and combobox_productos["values"][0] != "No hay productos":
            combobox_productos.set(combobox_productos["values"][0])
        else:
            combobox_productos.set("")  # Limpiar si no hay productos

        if combobox_materias_primas["values"] and combobox_materias_primas["values"][0] != "No hay materias primas":
            combobox_materias_primas.set(combobox_materias_primas["values"][0])
        else:
            combobox_materias_primas.set("")  # Limpiar si no hay materias primas

    # --- Botones de Acción ---
    btn_guardar_receta = tk.Button(frame_form_receta, text="Guardar Receta", command=guardar_receta, width=20,
                                   bg="lightgreen")
    btn_guardar_receta.grid(row=4, column=0, pady=10, padx=5, sticky="ew")

    btn_limpiar_campos = tk.Button(frame_form_receta, text="Limpiar Campos", command=limpiar_campos_receta, width=20,
                                   bg="lightgray")
    btn_limpiar_campos.grid(row=4, column=1, pady=10, padx=5, sticky="ew")

    btn_eliminar_receta = tk.Button(frame_form_receta, text="Eliminar Receta Seleccionada",
                                    command=eliminar_receta_seleccionada, width=30, bg="lightcoral")
    btn_eliminar_receta.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

    # --- Vinculación de Eventos y Carga Inicial ---
    lista_recetas.bind("<<ListboxSelect>>", seleccionar_receta)

    # Cargar datos al iniciar la ventana
    cargar_productos_y_materias_primas()
    cargar_recetas_en_gui()
    actualizar_lista_ingredientes_temp()  # Asegurarse de que la lista temporal esté vacía al inicio
