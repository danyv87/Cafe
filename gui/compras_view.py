import tkinter as tk
from tkinter import messagebox
from controllers.compras_controller import registrar_compra
from models.compra_detalle import CompraDetalle


def mostrar_ventana_compras():
    ventana = tk.Toplevel()
    ventana.title("Registrar Compra de Materia Prima")
    ventana.geometry("600x650")  # Ajusta el tamaño para acomodar el nuevo campo

    # --- Widgets de la Interfaz ---

    # Proveedor
    tk.Label(ventana, text="Nombre del Proveedor:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_proveedor = tk.Entry(ventana, width=50)
    entry_proveedor.pack()

    # Campo para el nombre de la materia prima
    tk.Label(ventana, text="Nombre de la Materia Prima/Artículo:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_nombre_materia_prima = tk.Entry(ventana, width=50)
    entry_nombre_materia_prima.pack()

    tk.Label(ventana, text="Cantidad:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_cantidad = tk.Entry(ventana, width=20)
    entry_cantidad.pack()

    # Nuevo campo para la descripción adicional
    tk.Label(ventana, text="Descripción Adicional:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_descripcion_adicional = tk.Entry(ventana, width=50)  # ¡Nuevo Entry!
    entry_descripcion_adicional.pack()

    tk.Label(ventana, text="Costo Unitario (Gs):", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
    entry_costo_unitario = tk.Entry(ventana, width=20)
    entry_costo_unitario.pack()

    label_total = tk.Label(ventana, text="Total Compra: Gs 0", font=("Helvetica", 14, "bold"), fg="blue")
    label_total.pack(pady=15)

    # Lista para almacenar objetos CompraDetalle para la compra actual
    compra_actual_items = []

    # Lista de productos agregados a la compra actual
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

    def actualizar_total_compra():
        """
        Calcula y actualiza el total de la compra actual.
        """
        total = sum(item.total for item in compra_actual_items)
        label_total.config(text=f"Total Compra: Gs {total:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def agregar_item_a_compra():
        """
        Agrega el item (materia prima/artículo) a la lista de la compra actual (como CompraDetalle).
        """
        try:
            nombre_item = entry_nombre_materia_prima.get().strip()
            cantidad_str = entry_cantidad.get()
            descripcion = entry_descripcion_adicional.get().strip()  # ¡Obtener la descripción!
            costo_str = entry_costo_unitario.get()

            if not nombre_item:
                messagebox.showwarning("Atención", "El nombre de la materia prima/artículo no puede estar vacío.")
                return

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
                producto_id=nombre_item,
                nombre_producto=nombre_item,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                descripcion_adicional=descripcion  # ¡Pasar la descripción al constructor!
            )
            compra_actual_items.append(detalle_compra)
            # Mostrar la descripción en el Listbox si existe
            display_text = f"{detalle_compra.nombre_producto} x {detalle_compra.cantidad}"
            if detalle_compra.descripcion_adicional:
                display_text += f" ({detalle_compra.descripcion_adicional})"
            display_text += f" = Gs {detalle_compra.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista_compra.insert(tk.END, display_text)

            actualizar_total_compra()
            entry_nombre_materia_prima.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_descripcion_adicional.delete(0, tk.END)  # ¡Limpiar el campo de descripción!
            entry_costo_unitario.delete(0, tk.END)
            entry_nombre_materia_prima.focus_set()
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
            f"¿Desea registrar la compra para '{proveedor}' con un total de Gs {sum(item.total for item in compra_actual_items):,.0f}?".replace(
                ",", "X").replace(".", ",").replace("X", ".")
        )
        if not confirmar_compra:
            messagebox.showinfo("Cancelado", "Registro de compra cancelado.")
            return

        try:
            compra_registrada = registrar_compra(proveedor, compra_actual_items)

            messagebox.showinfo("Compra Registrada",
                                f"Compra registrada con éxito para {proveedor}.\nTotal: Gs {compra_registrada.total:,.0f}".replace(
                                    ",", "X").replace(".", ",").replace("X", "."))

            compra_actual_items.clear()
            lista_compra.delete(0, tk.END)
            label_total.config(text="Total Compra: Gs 0")
            entry_proveedor.delete(0, tk.END)
            entry_nombre_materia_prima.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_descripcion_adicional.delete(0, tk.END)  # ¡Limpiar el campo de descripción!
            entry_costo_unitario.delete(0, tk.END)
            entry_proveedor.focus_set()
        except Exception as e:
            messagebox.showerror("Error al Registrar Compra", f"No se pudo registrar la compra.\nDetalle: {str(e)}")

    tk.Button(ventana, text="Agregar Item a Compra", command=agregar_item_a_compra, width=25).pack(pady=5)
    tk.Button(ventana, text="Registrar Compra", command=registrar_nueva_compra, width=25, bg="lightblue",
              fg="black").pack(pady=10)
