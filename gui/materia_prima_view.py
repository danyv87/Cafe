import tkinter as tk
from tkinter import messagebox, ttk
from controllers.materia_prima_controller import (
    listar_materias_primas,
    agregar_materia_prima,
    editar_materia_prima,
    eliminar_materia_prima,
    establecer_stock_materia_prima,
    obtener_materia_prima_por_id,
)
from controllers.recetas_controller import listar_recetas

def mostrar_ventana_materias_primas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Materias Primas")
    ventana.geometry("950x670")
    ventana.resizable(True, True)

    # --- Lista de materias primas ---
    frame_lista = tk.LabelFrame(ventana, text="Materias Primas", padx=5, pady=5)
    frame_lista.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

    scrollbar_lista = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
    lista = tk.Listbox(frame_lista, width=50, height=25, yscrollcommand=scrollbar_lista.set)
    scrollbar_lista.config(command=lista.yview)
    lista.grid(row=0, column=0, sticky="nsew")
    scrollbar_lista.grid(row=0, column=1, sticky="ns")

    def cargar_materias_primas():
        lista.delete(0, tk.END)
        materias_primas = listar_materias_primas()
        materias_primas.sort(key=lambda mp: mp.nombre.lower())
        if not materias_primas:
            lista.insert(tk.END, "No hay materias primas registradas.")
        else:
            for mp in materias_primas:
                lista.insert(
                    tk.END,
                    f"ID: {mp.id[:8]}... - {mp.nombre} | Unidad: {mp.unidad_medida} | Costo: Gs {mp.costo_unitario:,.0f} | Stock: {mp.stock:,.2f}",
                )

    cargar_materias_primas()

    # --- Sección Agregar ---
    frame_agregar = tk.LabelFrame(ventana, text="Agregar Materia Prima", padx=10, pady=10)
    frame_agregar.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
    for i in range(4): frame_agregar.grid_columnconfigure(i, weight=1)

    tk.Label(frame_agregar, text="Nombre:").grid(row=0, column=0, sticky="e")
    entry_nombre = tk.Entry(frame_agregar, width=18)
    entry_nombre.grid(row=0, column=1)

    tk.Label(frame_agregar, text="Unidad:").grid(row=0, column=2, sticky="e")
    entry_unidad = tk.Entry(frame_agregar, width=10)
    entry_unidad.grid(row=0, column=3)

    tk.Label(frame_agregar, text="Costo Unitario:").grid(row=1, column=0, sticky="e")
    entry_costo = tk.Entry(frame_agregar, width=12)
    entry_costo.grid(row=1, column=1)

    tk.Label(frame_agregar, text="Stock Inicial:").grid(row=1, column=2, sticky="e")
    entry_stock = tk.Entry(frame_agregar, width=10)
    entry_stock.grid(row=1, column=3)

    def agregar_mp():
        nombre = entry_nombre.get().strip()
        unidad = entry_unidad.get().strip()
        costo = entry_costo.get().strip()
        stock = entry_stock.get().strip()
        if not nombre or not unidad or not costo or not stock:
            messagebox.showwarning("Atención", "Complete todos los campos.")
            return
        try:
            costo = float(costo)
            stock = int(stock)
            if costo < 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Costo y stock deben ser números no negativos.")
            return
        try:
            agregar_materia_prima(nombre, unidad, costo, stock)
            cargar_materias_primas()
            entry_nombre.delete(0, tk.END)
            entry_unidad.delete(0, tk.END)
            entry_costo.delete(0, tk.END)
            entry_stock.delete(0, tk.END)
            messagebox.showinfo("Éxito", "Materia prima agregada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar.\nDetalle: {e}")

    tk.Button(frame_agregar, text="Agregar", width=14, command=agregar_mp, bg="lightgreen").grid(row=2, column=3, pady=7, sticky="e")

    # --- Sección Editar/Eliminar ---
    frame_editar = tk.LabelFrame(ventana, text="Editar / Eliminar Materia Prima", padx=10, pady=10)
    frame_editar.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
    for i in range(4): frame_editar.grid_columnconfigure(i, weight=1)

    tk.Label(frame_editar, text="ID:").grid(row=0, column=0, sticky="e")
    entry_id_editar = tk.Entry(frame_editar, width=18)
    entry_id_editar.grid(row=0, column=1)

    tk.Label(frame_editar, text="Nuevo Nombre:").grid(row=0, column=2, sticky="e")
    entry_nombre_editar = tk.Entry(frame_editar, width=18)
    entry_nombre_editar.grid(row=0, column=3)

    tk.Label(frame_editar, text="Unidad:").grid(row=1, column=0, sticky="e")
    entry_unidad_editar = tk.Entry(frame_editar, width=10)
    entry_unidad_editar.grid(row=1, column=1)

    tk.Label(frame_editar, text="Costo Unitario:").grid(row=1, column=2, sticky="e")
    entry_costo_unitario_editar = tk.Entry(frame_editar, width=10)
    entry_costo_unitario_editar.grid(row=1, column=3)

    tk.Label(frame_editar, text="Stock:").grid(row=2, column=0, sticky="e")
    entry_stock_editar = tk.Entry(frame_editar, width=10)
    entry_stock_editar.grid(row=2, column=1)

    def cargar_campos_editar(event=None):
        seleccion = lista.curselection()
        if not seleccion:
            return
        linea = lista.get(seleccion[0])
        if "ID:" not in linea:
            return
        id_mp = linea.split("ID: ")[1][:8]
        mp_obj = None
        for mp in listar_materias_primas():
            if mp.id.startswith(id_mp):
                mp_obj = mp
                break
        if not mp_obj:
            return
        entry_id_editar.delete(0, tk.END)
        entry_id_editar.insert(0, mp_obj.id)
        entry_nombre_editar.delete(0, tk.END)
        entry_nombre_editar.insert(0, mp_obj.nombre)
        entry_unidad_editar.delete(0, tk.END)
        entry_unidad_editar.insert(0, mp_obj.unidad_medida)
        entry_costo_unitario_editar.delete(0, tk.END)
        entry_costo_unitario_editar.insert(0, str(mp_obj.costo_unitario))
        entry_stock_editar.delete(0, tk.END)
        entry_stock_editar.insert(0, str(mp_obj.stock))

    lista.bind("<<ListboxSelect>>", cargar_campos_editar)

    def editar_mp():
        id_mp = entry_id_editar.get().strip()
        nombre = entry_nombre_editar.get().strip()
        unidad = entry_unidad_editar.get().strip()
        costo = entry_costo_unitario_editar.get().strip()
        stock = entry_stock_editar.get().strip()
        if not id_mp or not nombre or not unidad or not costo or not stock:
            messagebox.showwarning("Atención", "Complete todos los campos.")
            return
        try:
            costo = float(costo)
            stock = int(stock)
            if costo < 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Costo y stock deben ser números no negativos.")
            return
        try:
            editar_materia_prima(id_mp, nombre, unidad, costo, stock)
            cargar_materias_primas()
            messagebox.showinfo("Éxito", "Materia prima editada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar.\nDetalle: {e}")

    def eliminar_mp():
        id_mp = entry_id_editar.get().strip()
        if not id_mp:
            messagebox.showwarning("Atención", "Ingrese el ID de la materia prima a eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la materia prima {id_mp[:8]}...?"):
            try:
                eliminar_materia_prima(id_mp)
                cargar_materias_primas()
                messagebox.showinfo("Éxito", "Materia prima eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar.\nDetalle: {e}")

    tk.Button(frame_editar, text="Editar", width=14, command=editar_mp, bg="lightblue").grid(row=3, column=2, pady=7, sticky="e")
    tk.Button(frame_editar, text="Eliminar", width=14, command=eliminar_mp, bg="salmon").grid(row=3, column=3, pady=7, sticky="e")

    # --- Sección Forzar Stock ---
    frame_forzar = tk.LabelFrame(ventana, text="Forzar/Ajustar Stock", padx=10, pady=10)
    frame_forzar.grid(row=2, column=0, sticky="ew", padx=5, pady=3, columnspan=2)
    for i in range(4): frame_forzar.grid_columnconfigure(i, weight=1)

    tk.Label(frame_forzar, text="ID MP:").grid(row=0, column=0, sticky="e")
    entry_id_forzar = tk.Entry(frame_forzar, width=18)
    entry_id_forzar.grid(row=0, column=1)

    tk.Label(frame_forzar, text="Nuevo Stock:").grid(row=0, column=2, sticky="e")
    entry_forzar_stock = tk.Entry(frame_forzar, width=10)
    entry_forzar_stock.grid(row=0, column=3)

    def forzar_stock():
        id_mp = entry_id_forzar.get().strip()
        nuevo_stock = entry_forzar_stock.get().strip()
        if not id_mp or not nuevo_stock:
            messagebox.showwarning("Atención", "Complete ambos campos.")
            return
        try:
            nuevo_stock = float(nuevo_stock)
            if nuevo_stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El stock a forzar debe ser un número no negativo.")
            return
        if messagebox.askyesno("Confirmar", f"¿Está seguro de ajustar el stock de '{id_mp[:8]}' a {nuevo_stock}?"):
            try:
                establecer_stock_materia_prima(id_mp, nuevo_stock)
                cargar_materias_primas()
                messagebox.showinfo("Éxito", "Stock ajustado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ajustar el stock.\nDetalle: {e}")

    tk.Button(frame_forzar, text="Forzar Stock", width=14, command=forzar_stock, bg="orange").grid(row=1, column=3, pady=7, sticky="e")

    # --- Sección de Calcular consumo de materias primas por receta y lotes ---
    frame_calculo = tk.LabelFrame(ventana, text="Calcular Consumo de Materias Primas por Receta", padx=10, pady=10)
    frame_calculo.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
    for i in range(3): frame_calculo.grid_columnconfigure(i, weight=1)

    tk.Label(frame_calculo, text="Receta:").grid(row=0, column=0, sticky="e")

    def get_recetas_y_opciones():
        recetas = listar_recetas()
        opciones = [f"{getattr(r, 'nombre_producto', getattr(r, 'nombre', ''))} (ID: {getattr(r, 'id', '')[:8]})" for r in recetas]
        if not opciones:
            opciones = ["No hay recetas registradas"]
        return recetas, opciones

    recetas_lista, opciones_recetas = get_recetas_y_opciones()
    var_receta = tk.StringVar(frame_calculo)
    combobox_recetas = ttk.Combobox(frame_calculo, textvariable=var_receta, values=opciones_recetas, state="readonly", width=40)
    combobox_recetas.grid(row=0, column=1, padx=5, pady=2, sticky="w")
    combobox_recetas.current(0)
    if opciones_recetas[0] == "No hay recetas registradas":
        combobox_recetas.config(state="disabled")

    def refrescar_recetas():
        nonlocal recetas_lista
        recetas_lista, opciones = get_recetas_y_opciones()
        combobox_recetas["values"] = opciones
        combobox_recetas.current(0)
        var_receta.set(opciones[0])
        if opciones[0] == "No hay recetas registradas":
            combobox_recetas.config(state="disabled")
        else:
            combobox_recetas.config(state="readonly")

    tk.Button(frame_calculo, text="Refrescar recetas", command=refrescar_recetas).grid(row=0, column=2, padx=5)

    tk.Label(frame_calculo, text="Cantidad de lotes:").grid(row=1, column=0, sticky="e")
    entry_lotes = tk.Entry(frame_calculo, width=10)
    entry_lotes.insert(0, "1")
    entry_lotes.grid(row=1, column=1, padx=5, pady=2, sticky="w")

    label_consumo = tk.Label(frame_calculo, text="", justify="left", anchor="w", wraplength=550, fg="black")
    label_consumo.grid(row=3, column=0, columnspan=3, sticky="w")

    def calcular_consumo_receta():
        if var_receta.get() == "No hay recetas registradas":
            messagebox.showwarning("Atención", "Debe registrar al menos una receta para usar esta función.")
            return
        receta_nombre = var_receta.get()
        try:
            lotes = int(entry_lotes.get())
            if lotes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atención", "La cantidad de lotes debe ser un número entero positivo.")
            return
        rec_id = receta_nombre.split("ID: ")[-1].strip(")")
        receta_obj = None
        for r in recetas_lista:
            if getattr(r, "id", "")[:8] == rec_id:
                receta_obj = r
                break
        if not receta_obj:
            messagebox.showerror("Error", "No se pudo encontrar la receta seleccionada.")
            return
        texto = f"Consumo para {lotes} lote(s) de '{getattr(receta_obj, 'nombre_producto', getattr(receta_obj, 'nombre', '?'))}':\n"
        faltantes = []
        for ing in receta_obj.ingredientes:
            mp = obtener_materia_prima_por_id(ing["materia_prima_id"])
            cantidad_necesaria = ing["cantidad_necesaria"] * lotes
            nombre_mp = ing.get("nombre_materia_prima", mp.nombre if mp else "¿?")
            unidad = ing.get("unidad_medida", mp.unidad_medida if mp else "¿?")
            stock = mp.stock if mp else 0
            suficiente = stock >= cantidad_necesaria
            texto += f"- {nombre_mp}: se necesita {cantidad_necesaria:.2f} {unidad} (Stock actual: {stock:.2f})"
            if not suficiente:
                texto += "  ⚠️ INSUFICIENTE"
                faltantes.append(nombre_mp)
            texto += "\n"
        if not faltantes:
            texto += "\n✅ Hay suficientes materias primas para producir esa cantidad de lotes."
        else:
            texto += "\n⚠️ No hay suficiente stock para: " + ", ".join(faltantes)
        label_consumo.config(text=texto)

    tk.Button(frame_calculo, text="Calcular Consumo", width=20, bg="lightblue", command=calcular_consumo_receta).grid(row=2, column=1, pady=7, sticky="w")

    # Expandir columnas y filas principales para mejor visualización
    ventana.grid_rowconfigure(0, weight=1)
    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_rowconfigure(2, weight=0)
    ventana.grid_rowconfigure(3, weight=0)
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_columnconfigure(1, weight=1)