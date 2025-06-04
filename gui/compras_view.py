import tkinter as tk
from tkinter import messagebox
from controllers.compras_controller import registrar_compra
from models.compra_detalle import CompraDetalle
from controllers.materia_prima_controller import listar_materias_primas, \
    obtener_materia_prima_por_id  # ¡Nuevas importaciones!


def mostrar_ventana_compras():
    ventana = tk.Toplevel()
    ventana.title("Registrar Compra de Materia Prima")
    ventana.geometry("700x700")  # Ajusta el tamaño para acomodar los nuevos elementos

    # --- Widgets de la Interfaz ---

    # Proveedor
    tk.Label(ventana, text="Nombre del Proveedor:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_proveedor = tk.Entry(ventana, width=50)
    entry_proveedor.pack()

    # Buscador de Materia Prima
    tk.Label(ventana, text="Buscar Materia Prima:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_buscar_mp = tk.Entry(ventana, width=50)
    entry_buscar_mp.pack()

    tk.Label(ventana, text="Materias Primas disponibles:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))

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
    lista_compra = tk.Listbox(frame_compra_list, height=8, width=60, yscrollcommand=scrollbar_compra.set)
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

    def agregar_item_a_compra():
        """
        Agrega el item (materia prima) a la lista de la compra actual (como CompraDetalle).
        """
        try:
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

            cantidad_str = entry_cantidad.get()
            descripcion = entry_descripcion_adicional.get().strip()
            costo_str = entry_costo_unitario.get()

            if not cantidad_str.isdigit():
                messagebox.showerror("Error de Entrada", "La cantidad debe ser un número entero.")
                return

            cantidad = int(cantidad_str)
            if cantidad <= 0:
                messagebox.showerror("Error de Entrada", "La cantidad debe ser un número positivo.")
                return

            try:
                costo_unitario = float(costo_str)
            except ValueError:
                messagebox.showerror("Error de Entrada", "El costo unitario debe ser un número válido.")
                return

            if costo_unitario <= 0:
                messagebox.showerror("Error de Entrada", "El costo unitario debe ser un número positivo.")
                return

            detalle_compra = CompraDetalle(
                producto_id=materia_prima_encontrada.id,  # Ahora usamos el ID de la MateriaPrima
                nombre_producto=materia_prima_encontrada.nombre,  # Nombre de la MateriaPrima
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                descripcion_adicional=descripcion
            )
            compra_actual_items.append(detalle_compra)

            display_text = f"{detalle_compra.nombre_producto} x {detalle_compra.cantidad} {materia_prima_encontrada.unidad_medida}"
            if detalle_compra.descripcion_adicional:
                display_text += f" ({detalle_compra.descripcion_adicional})"
            display_text += f" = Gs {detalle_compra.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista_compra.insert(tk.END, display_text)

            actualizar_total_compra()
            entry_cantidad.delete(0, tk.END)
            entry_descripcion_adicional.delete(0, tk.END)
            entry_costo_unitario.delete(0, tk.END)
            entry_buscar_mp.delete(0, tk.END)  # Limpiar buscador de MP
            cargar_materias_primas_disponibles()  # Recargar lista de MP
            entry_buscar_mp.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar item a la compra: {e}")

    def registrar_nueva_compra():
        """
        Registra la compra completa.
        """
        proveedor = entry_proveedor.get().strip()
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
            compra_registrada = registrar_compra(proveedor, compra_actual_items)

            messagebox.showinfo("Compra Registrada",
                                f"Compra registrada con éxito para {proveedor}.\nTotal: Gs {compra_registrada.total:,.0f}".replace(
                                    ",", "X").replace(".", ",").replace("X", "."))

            # Limpiar todo para una nueva compra
            compra_actual_items.clear()
            lista_compra.delete(0, tk.END)
            label_total.config(text="Total Compra: Gs 0")
            entry_proveedor.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_descripcion_adicional.delete(0, tk.END)
            entry_costo_unitario.delete(0, tk.END)
            entry_buscar_mp.delete(0, tk.END)  # Limpiar buscador de MP
            cargar_materias_primas_disponibles()  # Recargar lista de MP
            entry_proveedor.focus_set()
        except ValueError as e:  # Captura errores específicos de ValueError (como stock insuficiente)
            messagebox.showerror("Error al Registrar Compra", str(e))
        except Exception as e:
            messagebox.showerror("Error al Registrar Compra", f"No se pudo registrar la compra.\nDetalle: {str(e)}")

    # --- Vinculación de Eventos y Carga Inicial ---
    entry_buscar_mp.bind("<KeyRelease>", on_buscar_mp)

    tk.Button(ventana, text="Agregar Item a Compra", command=agregar_item_a_compra, width=25).pack(pady=5)
    tk.Button(ventana, text="Registrar Compra", command=registrar_nueva_compra, width=25, bg="lightblue",
              fg="black").pack(pady=10)

    cargar_materias_primas_disponibles()  # Carga inicial de materias primas
