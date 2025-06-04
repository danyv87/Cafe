import tkinter as tk
from tkinter import messagebox
from controllers.materia_prima_controller import (
    listar_materias_primas,
    agregar_materia_prima,
    validar_materia_prima,
    obtener_materia_prima_por_id,  # Necesario para cargar datos al editar
    editar_materia_prima,  # Nueva función
    eliminar_materia_prima  # Nueva función
)


def mostrar_ventana_materias_primas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Materias Primas")
    ventana.geometry("700x700")  # Aumenta el tamaño para acomodar más campos y botones

    # --- Variables para los campos de edición ---
    materia_prima_seleccionada_id = tk.StringVar()

    # --- Widgets de la Interfaz ---

    # Frame para la lista de materias primas
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=100, yscrollcommand=scrollbar.set, exportselection=False)
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame para el formulario de Agregar
    frame_form_agregar = tk.LabelFrame(ventana, text="Agregar Nueva Materia Prima", padx=10, pady=10)
    frame_form_agregar.pack(pady=10, fill=tk.X)

    tk.Label(frame_form_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_nombre = tk.Entry(frame_form_agregar, width=40)
    entry_nombre.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame_form_agregar, text="Unidad de Medida:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_unidad_medida = tk.Entry(frame_form_agregar, width=40)
    entry_unidad_medida.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form_agregar, text="Costo Unitario (Gs):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_costo_unitario = tk.Entry(frame_form_agregar, width=40)
    entry_costo_unitario.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(frame_form_agregar, text="Stock Inicial:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    entry_stock_inicial = tk.Entry(frame_form_agregar, width=40)
    entry_stock_inicial.grid(row=3, column=1, padx=5, pady=2)

    # Frame para el formulario de Editar/Eliminar
    frame_form_editar = tk.LabelFrame(ventana, text="Editar / Eliminar Materia Prima Seleccionada", padx=10, pady=10)
    frame_form_editar.pack(pady=10, fill=tk.X)

    tk.Label(frame_form_editar, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_nombre_editar = tk.Entry(frame_form_editar, width=40)
    entry_nombre_editar.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame_form_editar, text="Unidad de Medida:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_unidad_medida_editar = tk.Entry(frame_form_editar, width=40)
    entry_unidad_medida_editar.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form_editar, text="Costo Unitario (Gs):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_costo_unitario_editar = tk.Entry(frame_form_editar, width=40)
    entry_costo_unitario_editar.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(frame_form_editar, text="Stock Actual:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    entry_stock_editar = tk.Entry(frame_form_editar, width=40)
    entry_stock_editar.grid(row=3, column=1, padx=5, pady=2)

    # --- Funciones ---

    def cargar_materias_primas():
        """
        Carga las materias primas desde el controlador y las muestra en el Listbox.
        """
        lista.delete(0, tk.END)
        materias_primas = listar_materias_primas()
        if not materias_primas:
            lista.insert(tk.END, "No hay materias primas registradas.")
        else:
            for mp in materias_primas:
                # Formatear números por separado para evitar afectar el ID
                costo_formateado = f"{mp.costo_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                stock_formateado = f"{mp.stock:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista.insert(tk.END, f"ID: {mp.id[:8]}... - {mp.nombre} ({mp.unidad_medida}) - Costo: Gs {costo_formateado} - Stock: {stock_formateado}")

    def agregar():
        """
        Función para agregar una nueva materia prima.
        Incluye validación y confirmación.
        """
        nombre = entry_nombre.get()
        unidad_medida = entry_unidad_medida.get()
        costo_unitario_str = entry_costo_unitario.get()
        stock_inicial_str = entry_stock_inicial.get()

        try:
            costo_unitario = float(costo_unitario_str)
            stock_inicial = int(stock_inicial_str)
        except ValueError:
            messagebox.showerror("Error de Entrada", "Costo unitario y Stock deben ser números válidos.")
            return

        es_valido, mensaje_error = validar_materia_prima(nombre, unidad_medida, costo_unitario, stock_inicial)
        if not es_valido:
            messagebox.showerror("Error de Validación", mensaje_error)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Adición",
            f"¿Desea agregar la materia prima '{nombre}' con stock {stock_inicial}?"
        )
        if confirmar:
            try:
                agregar_materia_prima(nombre, unidad_medida, costo_unitario, stock_inicial)
                cargar_materias_primas()
                entry_nombre.delete(0, tk.END)
                entry_unidad_medida.delete(0, tk.END)
                entry_costo_unitario.delete(0, tk.END)
                entry_stock_inicial.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Materia prima agregada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Agregar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        else:
            messagebox.showinfo("Cancelado", "Adición de materia prima cancelada.")

    def seleccionar_materia_prima(event):
        """
        Función que se ejecuta al seleccionar una materia prima en el Listbox.
        Carga los datos de la materia prima seleccionada en los campos de edición.
        """
        try:
            seleccion_indices = lista.curselection()
            if not seleccion_indices:
                return

            linea_seleccionada = lista.get(seleccion_indices[0])
            print(f"DEBUG: Línea seleccionada: {linea_seleccionada}")  # DEBUG PRINT
            # El ID abreviado ahora debería estar limpio de comas/puntos extraños
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')
            print(f"DEBUG: ID abreviado extraído: {id_abrev}")  # DEBUG PRINT

            materias_primas_cargadas = listar_materias_primas()
            print(f"DEBUG: IDs de materias primas cargadas del controlador: {[mp.id for mp in materias_primas_cargadas]}")  # DEBUG PRINT

            materia_prima_encontrada = None
            for mp in materias_primas_cargadas:
                print(
                    f"DEBUG: Comparando '{mp.id}' (completo) con '{id_abrev}' (abreviado). startswith: {mp.id.startswith(id_abrev)}")  # DEBUG PRINT
                if mp.id.startswith(id_abrev):
                    materia_prima_encontrada = mp
                    break

            if materia_prima_encontrada:
                materia_prima_seleccionada_id.set(materia_prima_encontrada.id)
                entry_nombre_editar.delete(0, tk.END)
                entry_nombre_editar.insert(0, materia_prima_encontrada.nombre)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_unidad_medida_editar.insert(0, materia_prima_encontrada.unidad_medida)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_costo_unitario_editar.insert(0, str(materia_prima_encontrada.costo_unitario))
                entry_stock_editar.delete(0, tk.END)
                entry_stock_editar.insert(0, str(materia_prima_encontrada.stock))
            else:
                messagebox.showwarning("Error", "No se pudo encontrar la materia prima completa.")
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar la materia prima: {e}")
            materia_prima_seleccionada_id.set("")
            entry_nombre_editar.delete(0, tk.END)
            entry_unidad_medida_editar.delete(0, tk.END)
            entry_costo_unitario_editar.delete(0, tk.END)
            entry_stock_editar.delete(0, tk.END)

    def editar():
        """
        Función para editar una materia prima existente.
        """
        id_a_editar = materia_prima_seleccionada_id.get()
        if not id_a_editar:
            messagebox.showwarning("Atención", "Seleccione una materia prima de la lista para editar.")
            return

        nuevo_nombre = entry_nombre_editar.get()
        nueva_unidad_medida = entry_unidad_medida_editar.get()
        nuevo_costo_unitario_str = entry_costo_unitario_editar.get()
        nuevo_stock_str = entry_stock_editar.get()

        try:
            nuevo_costo_unitario = float(nuevo_costo_unitario_str)
            nuevo_stock = int(nuevo_stock_str)
        except ValueError:
            messagebox.showerror("Error de Entrada", "El costo unitario y el stock deben ser números válidos.")
            return

        es_valido, mensaje_error = validar_materia_prima(nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario,
                                                         nuevo_stock)
        if not es_valido:
            messagebox.showerror("Error de Validación", mensaje_error)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Edición",
            f"¿Desea guardar los cambios para '{nuevo_nombre}'?"
        )
        if confirmar:
            try:
                editar_materia_prima(id_a_editar, nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario, nuevo_stock)
                cargar_materias_primas()
                # Limpiar campos de edición después de editar
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Materia prima editada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Editar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al editar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Edición de materia prima cancelada.")

    def eliminar():
        """
        Función para eliminar una materia prima.
        """
        id_a_eliminar = materia_prima_seleccionada_id.get()
        if not id_a_eliminar:
            messagebox.showwarning("Atención", "Seleccione una materia prima de la lista para eliminar.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar esta materia prima? Esta acción no se puede deshacer."
        )
        if confirmar:
            try:
                eliminar_materia_prima(id_a_eliminar)
                cargar_materias_primas()
                # Limpiar campos de edición después de eliminar
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Materia prima eliminada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Eliminar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Eliminación de materia prima cancelada.")

    # --- Vinculación de Eventos y Botones ---
    tk.Button(frame_form_agregar, text="Agregar Materia Prima", command=agregar, width=25).grid(row=4, column=0,
                                                                                                columnspan=2, pady=10)

    tk.Button(frame_form_editar, text="Editar Materia Prima", command=editar, width=20, bg="lightblue").grid(row=4,
                                                                                                             column=0,
                                                                                                             pady=5,
                                                                                                             padx=5)
    tk.Button(frame_form_editar, text="Eliminar Materia Prima", command=eliminar, width=20, bg="lightcoral").grid(row=4,
                                                                                                                  column=1,
                                                                                                                  pady=5,
                                                                                                                  padx=5)

    lista.bind("<<ListboxSelect>>", seleccionar_materia_prima)

    # Carga las materias primas al abrir la ventana
    cargar_materias_primas()
