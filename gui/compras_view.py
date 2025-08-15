import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime
from controllers.compras_controller import registrar_compra
from models.compra_detalle import CompraDetalle
from controllers.materia_prima_controller import listar_materias_primas, obtener_materia_prima_por_id


def mostrar_ventana_compras():
    ventana = tk.Toplevel()
    ventana.title("Registrar Compra de Materia Prima")
    ventana.geometry("800x850")  # Ajusta el tamaño para acomodar los nuevos elementos

    # --- Variables para el control de edición ---
    # Almacena el índice del ítem seleccionado en lista_compra para editar
    selected_item_index = -1

    # --- Widgets de la Interfaz ---

    # Proveedor
    tk.Label(ventana, text="Nombre del Proveedor:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_proveedor = tk.Entry(ventana, width=50)
    entry_proveedor.pack()

    # Fecha de la compra (opcional)
    tk.Label(ventana, text="Fecha de la compra (opcional):", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    fecha_hoy = datetime.date.today()
    date_entry = DateEntry(
        ventana,
        width=50,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        year=fecha_hoy.year,
        month=fecha_hoy.month,
        day=fecha_hoy.day
    )
    date_entry.pack()

    # Buscador de Materia Prima
    tk.Label(ventana, text="Buscar Materia Prima:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_buscar_mp = tk.Entry(ventana, width=50)
    entry_buscar_mp.pack()

    tk.Label(ventana, text="Materias Primas disponibles:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    # Mensaje de clarificación para el usuario
    tk.Label(ventana, text="Para comprar nuevas materias primas, regístralas primero en 'Gestionar Materias Primas'.",
             font=("Helvetica", 9, "italic"), fg="gray").pack(pady=(0, 5))

    # Frame para el Listbox de materias primas y su Scrollbar
    frame_mp_list = tk.Frame(ventana)
    frame_mp_list.pack(pady=5, fill=tk.BOTH, expand=True)

    scrollbar_mp = tk.Scrollbar(frame_mp_list, orient=tk.VERTICAL)
    lista_materias_primas = tk.Listbox(frame_mp_list, height=6, width=60, yscrollcommand=scrollbar_mp.set,
                                       exportselection=False)
    scrollbar_mp.config(command=lista_materias_primas.yview)

    scrollbar_mp.pack(side=tk.RIGHT, fill=tk.Y)
    lista_materias_primas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(ventana, text="Cantidad:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_cantidad = tk.Entry(ventana, width=20)
    entry_cantidad.pack()

    tk.Label(ventana, text="Descripción Adicional (Opcional):", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_descripcion_adicional = tk.Entry(ventana, width=50)
    entry_descripcion_adicional.pack()

    tk.Label(ventana, text="Costo Unitario (Gs):", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_costo_unitario = tk.Entry(ventana, width=20)
    entry_costo_unitario.pack()

    label_total = tk.Label(ventana, text="Total Compra: Gs 0", font=("Helvetica", 14, "bold"), fg="blue")
    label_total.pack(pady=15)

    # Lista para almacenar objetos CompraDetalle para la compra actual
    compra_actual_items = []

    # Lista de materias primas agregadas a la compra actual
    tk.Label(ventana, text="Items en la compra actual:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))

    # Frame para el Listbox de la compra actual y su Scrollbar
    frame_compra_list = tk.Frame(ventana)
    frame_compra_list.pack(pady=5, fill=tk.BOTH, expand=True)

    scrollbar_compra = tk.Scrollbar(frame_compra_list, orient=tk.VERTICAL)
    lista_compra = tk.Listbox(frame_compra_list, height=8, width=60, yscrollcommand=scrollbar_compra.set,
                              exportselection=False)
    scrollbar_compra.config(command=lista_compra.yview)

    scrollbar_compra.pack(side=tk.RIGHT, fill=tk.Y)
    lista_compra.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # --- Funciones ---

    def cargar_materias_primas_disponibles(filtro=""):
        """
        Carga las materias primas disponibles en el Listbox, aplicando un filtro si se proporciona.
        """
        lista_materias_primas.delete(0, tk.END)
        filtro = filtro.lower()
        materias_primas_filtradas = []
        all_materias_primas = listar_materias_primas()
        for mp in all_materias_primas:
            if filtro in mp.nombre.lower():
                materias_primas_filtradas.append(mp)

        if not materias_primas_filtradas:
            lista_materias_primas.insert(tk.END, "No se encontraron materias primas.")
        else:
            for mp in materias_primas_filtradas:
                lista_materias_primas.insert(tk.END, f"ID: {mp.id[:8]}... - {mp.nombre} ({mp.unidad_medida}) - Stock: {mp.stock}")

        if lista_materias_primas.size() > 0:
            lista_materias_primas.selection_set(0)  # Selecciona el primer elemento por defecto

    def on_buscar_mp(event):
        """
        Evento que se dispara al escribir en el campo de búsqueda de materias primas.
        Actualiza la lista de materias primas disponibles.
        """
        cargar_materias_primas_disponibles(entry_buscar_mp.get())

    def actualizar_total_compra():
        """
        Calcula y actualiza el total de la compra actual.
        """
        total = sum(item.total for item in compra_actual_items)
        label_total.config(text=f"Total Compra: Gs {total:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def actualizar_lista_compra_gui():
        """
        Actualiza el Listbox que muestra los ítems de la compra actual.
        """
        lista_compra.delete(0, tk.END)
        for item in compra_actual_items:
            # Obtener la unidad de medida de la materia prima original
            mp_original = obtener_materia_prima_por_id(item.producto_id)
            unidad_medida_display = mp_original.unidad_medida if mp_original else "unidad"

            display_text = f"{item.nombre_producto} x {item.cantidad} {unidad_medida_display}"
            if item.descripcion_adicional:
                display_text += f" ({item.descripcion_adicional})"
            display_text += f" = Gs {item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista_compra.insert(tk.END, display_text)
        actualizar_total_compra()

    def agregar_o_editar_item_a_compra():
        """
        Agrega un nuevo ítem o edita uno existente en la lista de la compra actual.
        """
        nonlocal selected_item_index  # Para modificar la variable en el scope superior

        try:
            cantidad_str = entry_cantidad.get().strip()
            descripcion = entry_descripcion_adicional.get().strip()
            costo_str = entry_costo_unitario.get().strip()

            # --- Validaciones de entrada ---
            if not cantidad_str:
                messagebox.showerror("Error de Entrada", "La cantidad no puede estar vacía.")
                return
            if not costo_str:
                messagebox.showerror("Error de Entrada", "El costo unitario no puede estar vacío.")
                return

            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    messagebox.showerror("Error de Entrada", "La cantidad debe ser un número entero positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error de Entrada", "La cantidad debe ser un número entero válido.")
                return

            try:
                costo_unitario = float(costo_str)
                if costo_unitario <= 0:
                    messagebox.showerror("Error de Entrada", "El costo unitario debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error de Entrada", "El costo unitario debe ser un número válido.")
                return

            if selected_item_index != -1:  # Estamos editando un ítem existente
                item_a_editar = compra_actual_items[selected_item_index]
                item_a_editar.cantidad = cantidad
                item_a_editar.costo_unitario = costo_unitario
                item_a_editar.descripcion_adicional = descripcion
                item_a_editar.total = round(cantidad * costo_unitario, 2)  # Recalcular total
                messagebox.showinfo("Éxito", "Ítem de compra editado correctamente.")
                selected_item_index = -1  # Resetear el índice de selección
            else:  # Estamos agregando un nuevo ítem
                seleccion_indices = lista_materias_primas.curselection()
                if not seleccion_indices:
                    messagebox.showwarning("Atención", "Seleccione una materia prima de la lista disponible.")
                    return

                linea_seleccionada = lista_materias_primas.get(seleccion_indices[0])
                mp_id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

                materia_prima_encontrada = None
                for mp in listar_materias_primas():
                    if mp.id.startswith(mp_id_abrev):
                        materia_prima_encontrada = mp
                        break

                if not materia_prima_encontrada:
                    messagebox.showerror("Error", "No se pudo encontrar la materia prima original. Intente de nuevo.")
                    return

                detalle_compra = CompraDetalle(
                    producto_id=materia_prima_encontrada.id,
                    nombre_producto=materia_prima_encontrada.nombre,
                    cantidad=cantidad,
                    costo_unitario=costo_unitario,
                    descripcion_adicional=descripcion
                )
                compra_actual_items.append(detalle_compra)
                messagebox.showinfo("Éxito", "Ítem de compra agregado correctamente.")

            actualizar_lista_compra_gui()  # Refrescar la lista en la GUI
            entry_cantidad.delete(0, tk.END)
            entry_descripcion_adicional.delete(0, tk.END)
            entry_costo_unitario.delete(0, tk.END)
            entry_buscar_mp.delete(0, tk.END)  # Limpiar buscador de MP
            cargar_materias_primas_disponibles()  # Recargar lista de MP
            entry_buscar_mp.focus_set()
            lista_compra.selection_clear(0, tk.END)  # Limpiar selección en la lista de compra

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar/editar item a la compra: {e}")

    def seleccionar_item_compra(event):
        """
        Carga los datos de un ítem seleccionado de la lista de compra actual en los campos de entrada.
        """
        nonlocal selected_item_index
        try:
            seleccion_indices = lista_compra.curselection()
            if not seleccion_indices:
                selected_item_index = -1
                return

            selected_item_index = seleccion_indices[0]
            item_seleccionado = compra_actual_items[selected_item_index]

            entry_cantidad.delete(0, tk.END)
            entry_cantidad.insert(0, str(item_seleccionado.cantidad))
            entry_descripcion_adicional.delete(0, tk.END)
            entry_descripcion_adicional.insert(0, item_seleccionado.descripcion_adicional)
            entry_costo_unitario.delete(0, tk.END)
            entry_costo_unitario.insert(0, str(item_seleccionado.costo_unitario))

        except Exception as e:
            messagebox.showerror("Error de Selección", f"No se pudo cargar el ítem para edición: {e}")
            selected_item_index = -1  # Resetear si hay un error

    def quitar_item_compra():
        """
        Quita el ítem seleccionado de la lista de compra actual.
        """
        nonlocal selected_item_index
        try:
            seleccion_indices = lista_compra.curselection()
            if not seleccion_indices:
                messagebox.showwarning("Atención", "Seleccione un ítem de la compra actual para quitar.")
                return

            confirmar = messagebox.askyesno(
                "Confirmar Eliminación",
                "¿Está seguro de que desea quitar este ítem de la compra actual?"
            )
            if confirmar:
                indice = seleccion_indices[0]
                del compra_actual_items[indice]
                actualizar_lista_compra_gui()
                messagebox.showinfo("Éxito", "Ítem quitado correctamente.")
                selected_item_index = -1  # Resetear el índice de selección
                # Limpiar campos de entrada después de quitar
                entry_cantidad.delete(0, tk.END)
                entry_descripcion_adicional.delete(0, tk.END)
                entry_costo_unitario.delete(0, tk.END)
                entry_buscar_mp.delete(0, tk.END)
                cargar_materias_primas_disponibles()
            else:
                messagebox.showinfo("Cancelado", "Operación cancelada.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al quitar ítem: {e}")

    def registrar_nueva_compra():
        """
        Registra la compra completa.
        """
        proveedor = entry_proveedor.get().strip()
        fecha_seleccionada = date_entry.get().strip()
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        if fecha_seleccionada:
            fecha = f"{fecha_seleccionada} {hora_actual}"
        else:
            fecha = ""
        if not proveedor:
            messagebox.showwarning("Atención", "Por favor, ingrese el nombre del proveedor.")
            return
        if not compra_actual_items:
            messagebox.showwarning("Atención", "No hay items en la compra actual.")
            return

        confirmar_compra = messagebox.askyesno(
            "Confirmar Compra",
            f"¿Desea registrar la compra para '{proveedor}' con un total de Gs {sum(item.total for item in compra_actual_items):,.0f}?".replace(",", "X").replace(".", ",").replace("X",".")
        )
        if not confirmar_compra:
            messagebox.showinfo("Cancelado", "Registro de compra cancelado.")
            return

        try:
            compra_registrada = registrar_compra(proveedor, compra_actual_items, fecha=fecha)

            messagebox.showinfo("Compra Registrada",
                                f"Compra registrada con éxito para {proveedor}.\nTotal: Gs {compra_registrada.total:,.0f}".replace(
                                    ",", "X").replace(".", ",").replace("X", "."))

            # Limpiar todo para una nueva compra
            compra_actual_items.clear()
            actualizar_lista_compra_gui()  # Refrescar la lista vacía
            label_total.config(text="Total Compra: Gs 0")
            entry_proveedor.delete(0, tk.END)
            date_entry.set_date(fecha_hoy)
            entry_cantidad.delete(0, tk.END)
            entry_descripcion_adicional.delete(0, tk.END)
            entry_costo_unitario.delete(0, tk.END)
            entry_buscar_mp.delete(0, tk.END)  # Limpiar buscador de MP
            cargar_materias_primas_disponibles()  # Recargar lista de MP
            entry_proveedor.focus_set()
            selected_item_index = -1  # Resetear el índice de selección
        except ValueError as e:  # Captura errores específicos de ValueError (como stock insuficiente)
            messagebox.showerror("Error al Registrar Compra", str(e))
        except Exception as e:
            messagebox.showerror("Error al Registrar Compra", f"No se pudo registrar la compra.\nDetalle: {str(e)}")

    # --- Vinculación de Eventos y Carga Inicial ---
    entry_buscar_mp.bind("<KeyRelease>", on_buscar_mp)
    lista_compra.bind("<<ListboxSelect>>", seleccionar_item_compra)  # Vincula la selección de ítem

    tk.Button(ventana, text="Agregar/Editar Item", command=agregar_o_editar_item_a_compra, width=25,
              bg="lightgray").pack(pady=5)
    tk.Button(ventana, text="Quitar Item Seleccionado", command=quitar_item_compra, width=25, bg="lightcoral").pack(
        pady=5)
    tk.Button(ventana, text="Registrar Compra", command=registrar_nueva_compra, width=25, bg="lightblue",
              fg="black").pack(pady=10)

    cargar_materias_primas_disponibles()  # Carga inicial de materias primas
