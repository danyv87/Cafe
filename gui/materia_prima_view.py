import tkinter as tk
from tkinter import messagebox
from controllers.materia_prima_controller import (
    listar_materias_primas,
    agregar_materia_prima,
    validar_materia_prima,
    obtener_materia_prima_por_id,
    editar_materia_prima,
    eliminar_materia_prima,
    establecer_stock_materia_prima
)
from controllers.recetas_controller import listar_recetas

def obtener_nombre_producto_y_rendimiento(receta):
    # Soporta tanto objeto como dict
    if hasattr(receta, "nombre_producto") and getattr(receta, "nombre_producto"):
        nombre = getattr(receta, "nombre_producto")
    elif hasattr(receta, "nombre") and getattr(receta, "nombre"):
        nombre = getattr(receta, "nombre")
    elif isinstance(receta, dict):
        nombre = receta.get("nombre_producto") or receta.get("nombre") or "Producto"
    else:
        nombre = "Producto"
    # Buscar el campo correcto 'rendimiento'
    if hasattr(receta, "rendimiento") and getattr(receta, "rendimiento", None) is not None:
        rendimiento = getattr(receta, "rendimiento")
    elif isinstance(receta, dict):
        rendimiento = receta.get("rendimiento")
    else:
        rendimiento = None
    return nombre, rendimiento

def obtener_materias_primas_faltantes():
    recetas = listar_recetas()
    materias_primas = {mp.id: mp for mp in listar_materias_primas()}
    faltantes = []
    for receta in recetas:
        nombre_producto, rendimiento = obtener_nombre_producto_y_rendimiento(receta)
        for ingrediente in receta.ingredientes:
            mp_id = ingrediente["materia_prima_id"]
            cantidad_necesaria = ingrediente["cantidad_necesaria"]
            mp = materias_primas.get(mp_id)
            if mp and mp.stock < cantidad_necesaria:
                faltantes.append({
                    "materia_prima": mp.nombre,
                    "producto": nombre_producto,
                    "rendimiento": rendimiento,
                    "stock": mp.stock,
                    "necesario": cantidad_necesaria,
                    "unidad": mp.unidad_medida
                })
    return faltantes

def mostrar_ventana_materias_primas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Materias Primas")
    ventana.geometry("950x900")

    materia_prima_seleccionada_id = tk.StringVar()

    # Frame para la lista de materias primas
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=80, yscrollcommand=scrollbar.set, exportselection=False)
    scrollbar.config(command=lista.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame para el formulario de Agregar
    frame_form_agregar = tk.LabelFrame(ventana, text="Agregar Nueva Materia Prima", padx=10, pady=10)
    frame_form_agregar.pack(pady=10, fill=tk.X)

    # Nombre
    tk.Label(frame_form_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_nombre = tk.Entry(frame_form_agregar, width=40)
    entry_nombre.grid(row=0, column=1, padx=5, pady=2)
    tk.Label(frame_form_agregar, text="Ej: Granos de Café, Leche, Azúcar", fg="gray").grid(row=0, column=2, padx=5, pady=2, sticky="w")

    # Unidad de Medida
    tk.Label(frame_form_agregar, text="Unidad de Medida:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_unidad_medida = tk.Entry(frame_form_agregar, width=40)
    entry_unidad_medida.grid(row=1, column=1, padx=5, pady=2)
    tk.Label(frame_form_agregar, text="Ej: kg, litros, unidades, gramos", fg="gray").grid(row=1, column=2, padx=5, pady=2, sticky="w")

    # Costo Unitario (Gs)
    tk.Label(frame_form_agregar, text="Costo Unitario (Gs):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_costo_unitario = tk.Entry(frame_form_agregar, width=40)
    entry_costo_unitario.grid(row=2, column=1, padx=5, pady=2)
    tk.Label(frame_form_agregar, text="Costo por unidad de compra. Ej: 5000 (para 1 kg)", fg="gray").grid(row=2, column=2, padx=5, pady=2, sticky="w")

    # Stock Inicial
    tk.Label(frame_form_agregar, text="Stock Inicial:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    entry_stock_inicial = tk.Entry(frame_form_agregar, width=40)
    entry_stock_inicial.grid(row=3, column=1, padx=5, pady=2)
    entry_stock_inicial.insert(0, "0")
    tk.Label(frame_form_agregar, text="Cantidad inicial en inventario. Ej: 10 (para 10 kg)", fg="gray").grid(row=3, column=2, padx=5, pady=2, sticky="w")

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

    # Frame para Forzar Ajuste de Stock
    frame_forzar_stock = tk.LabelFrame(ventana, text="Forzar Ajuste de Stock", padx=10, pady=10)
    frame_forzar_stock.pack(pady=10, fill=tk.X)

    tk.Label(frame_forzar_stock, text="Forzar Stock a:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_forzar_stock = tk.Entry(frame_forzar_stock, width=20)
    entry_forzar_stock.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    # Sección de materias primas faltantes para recetas y rendimiento
    frame_faltantes = tk.LabelFrame(ventana, text="⚠ Materias Primas Insuficientes para Recetas", padx=10, pady=8)
    frame_faltantes.pack(pady=8, fill=tk.X)

    label_faltantes = tk.Label(frame_faltantes, text="", fg="red", justify="left", anchor="w")
    label_faltantes.pack(anchor="w")

    def actualizar_faltantes():
        faltantes = obtener_materias_primas_faltantes()
        if faltantes:
            texto = ""
            for f in faltantes:
                texto += f"- {f['materia_prima']} (stock: {f['stock']} {f['unidad']}), se necesita {f['necesario']} para '{f['producto']}'"
                # Mostrar el rendimiento si existe y es diferente de None, "", 0
                if f['rendimiento'] not in (None, "", 0):
                    texto += f" (Rinde: {f['rendimiento']} unidades por lote)"
                texto += "\n"
            label_faltantes.config(text=texto, fg="red")
        else:
            label_faltantes.config(text="Todas las materias primas alcanzan para al menos una unidad de cada producto.", fg="green")

    def cargar_materias_primas():
        lista.delete(0, tk.END)
        materias_primas = listar_materias_primas()
        if not materias_primas:
            lista.insert(tk.END, "No hay materias primas registradas.")
        else:
            for mp in materias_primas:
                costo_formateado = f"{mp.costo_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                stock_formateado = f"{mp.stock:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lista.insert(tk.END, f"ID: {mp.id[:8]}... - {mp.nombre} ({mp.unidad_medida}) - Costo: Gs {costo_formateado} - Stock: {stock_formateado}")
        actualizar_faltantes()

    def agregar():
        nombre = entry_nombre.get()
        unidad_medida = entry_unidad_medida.get()
        costo_str = entry_costo_unitario.get()
        stock_inicial_str = entry_stock_inicial.get()

        try:
            costo_unitario = float(costo_str)
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
                entry_stock_inicial.insert(0, "0")
                messagebox.showinfo("Éxito", "Materia prima agregada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Agregar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        else:
            messagebox.showinfo("Cancelado", "Adición de materia prima cancelada.")

    def seleccionar_materia_prima(event):
        try:
            seleccion_indices = lista.curselection()
            if not seleccion_indices:
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                entry_forzar_stock.delete(0, tk.END)
                return

            linea_seleccionada = lista.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            materias_primas_cargadas = listar_materias_primas()

            mp_encontrada = None
            for mp in materias_primas_cargadas:
                if mp.id.startswith(id_abrev):
                    mp_encontrada = mp
                    break

            if mp_encontrada:
                materia_prima_seleccionada_id.set(mp_encontrada.id)
                entry_nombre_editar.delete(0, tk.END)
                entry_nombre_editar.insert(0, mp_encontrada.nombre)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_unidad_medida_editar.insert(0, mp_encontrada.unidad_medida)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_costo_unitario_editar.insert(0, str(mp_encontrada.costo_unitario))
                entry_stock_editar.delete(0, tk.END)
                entry_stock_editar.insert(0, str(mp_encontrada.stock))
                entry_forzar_stock.delete(0, tk.END)
                entry_forzar_stock.insert(0, str(mp_encontrada.stock))
            else:
                messagebox.showwarning("Error", "No se pudo encontrar la materia prima completa.")
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                entry_forzar_stock.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar la materia prima: {e}")
            materia_prima_seleccionada_id.set("")
            entry_nombre_editar.delete(0, tk.END)
            entry_unidad_medida_editar.delete(0, tk.END)
            entry_costo_unitario_editar.delete(0, tk.END)
            entry_stock_editar.delete(0, tk.END)
            entry_forzar_stock.delete(0, tk.END)

    lista.bind("<<ListboxSelect>>", seleccionar_materia_prima)

    def editar():
        id_a_editar = materia_prima_seleccionada_id.get()
        if not id_a_editar:
            messagebox.showwarning("Atención", "Seleccione una materia prima de la lista para editar.")
            return

        nuevo_nombre = entry_nombre_editar.get()
        nueva_unidad_medida = entry_unidad_medida_editar.get()
        nuevo_costo_str = entry_costo_unitario_editar.get()
        nuevo_stock_str = entry_stock_editar.get()

        try:
            nuevo_costo_unitario = float(nuevo_costo_str)
            nuevo_stock = int(nuevo_stock_str)
        except ValueError:
            messagebox.showerror("Error de Entrada", "El costo unitario y el stock deben ser números válidos.")
            return

        es_valido, mensaje_error = validar_materia_prima(nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario, nuevo_stock)
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
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                entry_forzar_stock.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Materia prima editada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Editar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al editar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Edición de materia prima cancelada.")

    def eliminar():
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
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                entry_forzar_stock.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Materia prima eliminada correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Eliminar", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Eliminación de materia prima cancelada.")

    def forzar_stock():
        id_a_forzar = materia_prima_seleccionada_id.get()
        if not id_a_forzar:
            messagebox.showwarning("Atención", "Seleccione una materia prima de la lista para forzar el stock.")
            return

        nuevo_stock_str = entry_forzar_stock.get()
        try:
            nuevo_stock = int(nuevo_stock_str)
            if nuevo_stock < 0:
                messagebox.showerror("Error de Entrada", "El stock a forzar debe ser un número entero no negativo.")
                return
        except ValueError:
            messagebox.showerror("Error de Entrada", "El stock a forzar debe ser un número entero válido.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Ajuste de Stock",
            f"¿Está seguro de que desea forzar el stock de la materia prima seleccionada a {nuevo_stock}?"
        )
        if confirmar:
            try:
                establecer_stock_materia_prima(id_a_forzar, nuevo_stock)
                cargar_materias_primas()
                materia_prima_seleccionada_id.set("")
                entry_nombre_editar.delete(0, tk.END)
                entry_unidad_medida_editar.delete(0, tk.END)
                entry_costo_unitario_editar.delete(0, tk.END)
                entry_stock_editar.delete(0, tk.END)
                entry_forzar_stock.delete(0, tk.END)
                messagebox.showinfo("Éxito", "Stock ajustado correctamente.")
            except ValueError as e:
                messagebox.showerror("Error al Forzar Stock", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al forzar el stock: {e}")
        else:
            messagebox.showinfo("Cancelado", "Ajuste de stock cancelado.")

    tk.Button(frame_form_agregar, text="Agregar Materia Prima", command=agregar, width=25).grid(row=4, column=0, columnspan=2, pady=5)
    tk.Button(frame_form_editar, text="Editar Materia Prima", command=editar, width=20, bg="lightblue").grid(row=4, column=0, pady=5, padx=5)
    tk.Button(frame_form_editar, text="Eliminar Materia Prima", command=eliminar, width=20, bg="lightcoral").grid(row=4, column=1, pady=5, padx=5)
    tk.Button(frame_forzar_stock, text="Forzar Stock", command=forzar_stock, width=20, bg="lightgoldenrod").grid(row=0, column=2, padx=5, pady=2, sticky="ew")

    cargar_materias_primas()