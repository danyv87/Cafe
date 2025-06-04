import tkinter as tk
from tkinter import messagebox
from controllers.gastos_adicionales_controller import (
    listar_gastos_adicionales,
    agregar_gasto_adicional,
    eliminar_gasto_adicional,
    validar_gasto_adicional
)


def mostrar_ventana_gastos_adicionales():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Gastos Adicionales")
    ventana.geometry("600x500")

    # --- Variables ---
    gasto_seleccionado_id = tk.StringVar()

    # --- Widgets de la Interfaz ---

    # Frame para la lista de gastos
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=80, yscrollcommand=scrollbar.set, exportselection=False)
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame para el formulario de Agregar
    frame_form_agregar = tk.LabelFrame(ventana, text="Registrar Nuevo Gasto Adicional", padx=10, pady=10)
    frame_form_agregar.pack(pady=10, fill=tk.X)

    tk.Label(frame_form_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_nombre = tk.Entry(frame_form_agregar, width=40)
    entry_nombre.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame_form_agregar, text="Monto (Gs):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_monto = tk.Entry(frame_form_agregar, width=40)
    entry_monto.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame_form_agregar, text="Descripción (Opcional):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_descripcion = tk.Entry(frame_form_agregar, width=40)
    entry_descripcion.grid(row=2, column=1, padx=5, pady=2)

    # --- Funciones ---

    def cargar_gastos():
        """
        Carga los gastos adicionales desde el controlador y los muestra en el Listbox.
        """
        lista.delete(0, tk.END)
        gastos = listar_gastos_adicionales()
        if not gastos:
            lista.insert(tk.END, "No hay gastos adicionales registrados.")
        else:
            for ga in gastos:
                monto_formateado = f"{ga.monto:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista.insert(tk.END, f"ID: {ga.id[:8]}... - {ga.nombre} - Monto: Gs {monto_formateado} - Fecha: {ga.fecha} - Desc: {ga.descripcion}")

    def agregar():
        """
        Función para agregar un nuevo gasto adicional.
        """
        nombre = entry_nombre.get()
        monto_str = entry_monto.get()
        descripcion = entry_descripcion.get()

        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error de Entrada", "El monto debe ser un número válido.")
            return

        es_valido, mensaje_error = validar_gasto_adicional(nombre, monto)
        if not es_valido:
            messagebox.showerror("Error de Validación", mensaje_error)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Registro",
            f"¿Desea registrar el gasto '{nombre}' por Gs {monto:,.0f}?"
        )
        if confirmar:
            try:
                agregar_gasto_adicional(nombre, monto, descripcion=descripcion)
                cargar_gastos()
                entry_nombre.delete(0, tk.END)
                entry_monto.delete(0, tk.END)
                entry_descripcion.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Gasto adicional registrado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Registrar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        else:
            messagebox.showinfo("Cancelado", "Registro de gasto adicional cancelado.")

    def seleccionar_gasto(event):
        """
        Función que se ejecuta al seleccionar un gasto en el Listbox.
        Almacena el ID del gasto seleccionado para futuras operaciones.
        """
        try:
            seleccion_indices = lista.curselection()
            if not seleccion_indices:
                gasto_seleccionado_id.set("")
                return

            linea_seleccionada = lista.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            gastos_cargados = listar_gastos_adicionales()
            gasto_encontrado = None
            for ga in gastos_cargados:
                if ga.id.startswith(id_abrev):
                    gasto_encontrado = ga
                    break

            if gasto_encontrado:
                gasto_seleccionado_id.set(gasto_encontrado.id)
            else:
                messagebox.showwarning("Error", "No se pudo encontrar el gasto completo.")
                gasto_seleccionado_id.set("")

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar el gasto: {e}")
            gasto_seleccionado_id.set("")

    lista.bind("<<ListboxSelect>>", seleccionar_gasto)

    def eliminar():
        """
        Función para eliminar un gasto adicional.
        """
        id_a_eliminar = gasto_seleccionado_id.get()
        if not id_a_eliminar:
            messagebox.showwarning("Atención", "Seleccione un gasto de la lista para eliminar.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este gasto? Esta acción no se puede deshacer."
        )
        if confirmar:
            try:
                eliminar_gasto_adicional(id_a_eliminar)
                cargar_gastos()
                gasto_seleccionado_id.set("")  # Limpiar selección
                messagebox.showinfo("Éxito", "Gasto adicional eliminado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Eliminar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Eliminación de gasto adicional cancelada.")

    # --- Botones de acción ---
    tk.Button(frame_form_agregar, text="Registrar Gasto", command=agregar, width=20).grid(row=3, column=0, columnspan=2,
                                                                                          pady=5)

    tk.Button(ventana, text="Eliminar Gasto Seleccionado", command=eliminar, width=30, bg="lightcoral").pack(pady=5)

    # Carga inicial de gastos
    cargar_gastos()

