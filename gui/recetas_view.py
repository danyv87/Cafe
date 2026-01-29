import tkinter as tk
from tkinter import messagebox, ttk
from controllers.productos_controller import listar_productos, obtener_producto_por_id
from controllers.materia_prima_controller import listar_materias_primas, obtener_materia_prima_por_id
from controllers.recetas_controller import (
    cargar_recetas,
    guardar_recetas,
    agregar_receta,
    obtener_receta_por_producto_id,
    editar_receta,
    eliminar_receta,
    validar_ingredientes_receta,
    validar_receta_completa  # Importar la nueva función de validación
)


def mostrar_ventana_recetas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Recetas")
    ventana.geometry("850x800")  # Aumenta el tamaño para acomodar todos los elementos y el nuevo texto

    # --- Variables de control ---
    producto_seleccionado_id = tk.StringVar()
    receta_actual_id = tk.StringVar()  # Para almacenar el ID de la receta que se está editando
    filtro_receta_var = tk.StringVar(value="Todos")  # Variable para el filtro de receta
    unidad_medida_seleccionada_mp = tk.StringVar(value="")  # Para mostrar la unidad de medida de la MP seleccionada
    unidad_medida_ingresada = tk.StringVar(value="")  # Para seleccionar unidad al cargar cantidad
    rendimiento_var = tk.StringVar(value="1")  # Nuevo: Para el rendimiento de la receta

    # Lista temporal para los ingredientes de la receta actual
    # Formato: [{"materia_prima_id": "uuid", "nombre_materia_prima": "Leche", "cantidad_necesaria": 150, "unidad_medida": "ml", "costo_unitario": 5000.0}]
    ingredientes_receta_actual = []
    ultimo_ingrediente_seleccionado = None

    # --- Funciones de Formato ---
    def format_guarani(value):
        """Formatea un valor numérico a formato de Guaraníes con separadores de miles."""
        return f"Gs {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # --- Funciones de Lógica (Definidas antes de los widgets que las usan) ---

    def cargar_productos_en_lista(filtro_texto="", filtro_tipo="Todos"):
        lista_productos.delete(0, tk.END)
        productos = listar_productos()
        if not productos:
            lista_productos.insert(tk.END, "No hay productos registrados.")
            return

        filtro_texto = filtro_texto.lower()
        productos_filtrados = []

        for p in productos:
            if filtro_texto in p.nombre.lower():
                receta_asociada = obtener_receta_por_producto_id(p.id)
                is_receta_associated = (receta_asociada is not None)

                if filtro_tipo == "Todos":
                    productos_filtrados.append((p, receta_asociada))
                elif filtro_tipo == "Sin Receta" and not is_receta_associated:
                    productos_filtrados.append((p, receta_asociada))
                elif filtro_tipo == "Con Receta" and is_receta_associated:
                    productos_filtrados.append((p, receta_asociada))

        if not productos_filtrados:
            lista_productos.insert(tk.END, "No se encontraron productos con el filtro aplicado.")
        else:
            for p, receta_asociada in productos_filtrados:
                receta_status = "(Sin Receta)" if not receta_asociada else ""
                lista_productos.insert(tk.END, f"ID: {p.id[:8]}... - {p.nombre} {receta_status}")

    def cargar_materias_primas_en_lista(filtro=""):
        lista_materias_primas.delete(0, tk.END)
        materias_primas = listar_materias_primas()
        if not materias_primas:
            lista_materias_primas.insert(tk.END, "No hay materias primas registradas.")
            return

        filtro = filtro.lower()
        mps_filtradas = [mp for mp in materias_primas if filtro in mp.nombre.lower()]

        if not mps_filtradas:
            lista_materias_primas.insert(tk.END, "No se encontraron materias primas.")
        else:
            for mp in mps_filtradas:
                lista_materias_primas.insert(tk.END, f"ID: {mp.id[:8]}... - {mp.nombre} ({mp.unidad_medida}) - Costo: {format_guarani(mp.costo_unitario)}")

    def actualizar_lista_receta_ingredientes():
        lista_receta_ingredientes.delete(0, tk.END)
        total_costo_receta = 0.0
        if not ingredientes_receta_actual:
            lista_receta_ingredientes.insert(tk.END, "No hay ingredientes en esta receta.")
        else:
            for item in ingredientes_receta_actual:
                total_costo_ingrediente = item['cantidad_necesaria'] * item['costo_unitario']
                total_costo_receta += total_costo_ingrediente
                lista_receta_ingredientes.insert(tk.END,
                                                 f"{item['cantidad_necesaria']} {item['unidad_medida']} de {item['nombre_materia_prima']} "f"(Costo Unit: {format_guarani(item['costo_unitario'])} / Total: {format_guarani(total_costo_ingrediente)})")
            lista_receta_ingredientes.insert(tk.END,
                                             "------------------------------------------------------------------")
            lista_receta_ingredientes.insert(tk.END, f"Costo Total de Receta: {format_guarani(total_costo_receta)}")

            try:
                rendimiento = float(rendimiento_var.get())
                if rendimiento > 0:
                    costo_por_unidad = total_costo_receta / rendimiento
                    lista_receta_ingredientes.insert(tk.END,
                                                     f"Costo por Unidad de Producto (basado en rendimiento): {format_guarani(costo_por_unidad)}")
            except ValueError:
                lista_receta_ingredientes.insert(tk.END, "Rendimiento inválido para calcular costo por unidad.")
            except ZeroDivisionError:
                lista_receta_ingredientes.insert(tk.END, "Rendimiento cero. No se puede calcular costo por unidad.")

    def on_producto_seleccionado(event):
        try:
            seleccion_indices = lista_productos.curselection()
            if not seleccion_indices:
                return

            linea_seleccionada = lista_productos.get(seleccion_indices[0])
            id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            productos_cargados = listar_productos()
            prod_encontrado = None
            for p in productos_cargados:
                if p.id.startswith(id_abrev):
                    prod_encontrado = p
                    break

            if prod_encontrado:
                producto_seleccionado_id.set(prod_encontrado.id)
                receta_existente = obtener_receta_por_producto_id(prod_encontrado.id)

                ingredientes_receta_actual.clear()
                receta_actual_id.set("")
                rendimiento_var.set("1")  # Resetear rendimiento por defecto
                text_procedimiento.delete("1.0", tk.END)

                if receta_existente:
                    receta_actual_id.set(receta_existente.id)
                    for ing_data in receta_existente.ingredientes:
                        mp = obtener_materia_prima_por_id(ing_data["materia_prima_id"])
                        if mp:
                            ing_data["costo_unitario"] = mp.costo_unitario
                            ing_data["unidad_medida"] = mp.unidad_medida
                        else:
                            ing_data["costo_unitario"] = 0.0
                        ingredientes_receta_actual.append(ing_data)
                    sincronizar_ingredientes_con_materias_primas()

                    if receta_existente.rendimiento is not None:
                        rendimiento_var.set(str(receta_existente.rendimiento))

                    if receta_existente.procedimiento:
                        text_procedimiento.insert(tk.END, receta_existente.procedimiento)

                    messagebox.showinfo("Receta Cargada", f"Receta para '{prod_encontrado.nombre}' cargada.")
                else:
                    messagebox.showinfo("Nueva Receta",
                                        f"No hay receta para '{prod_encontrado.nombre}'. Puedes crear una nueva.")

                actualizar_lista_receta_ingredientes()
            else:
                messagebox.showwarning("Error", "No se pudo encontrar el producto completo. Intente de nuevo.")
                producto_seleccionado_id.set("")
                ingredientes_receta_actual.clear()
                rendimiento_var.set("1")  # Resetear rendimiento
                text_procedimiento.delete("1.0", tk.END)
                actualizar_lista_receta_ingredientes()
        except Exception as e:
            messagebox.showerror("Error de Selección", f"Ocurrió un error al seleccionar el producto: {e}")

    def on_materia_prima_seleccionada(event):
        """
        Actualiza la etiqueta de unidad de medida cuando se selecciona una MP.
        """
        try:
            seleccion_indices = lista_materias_primas.curselection()
            if not seleccion_indices:
                unidad_medida_seleccionada_mp.set("")
                return

            linea_seleccionada = lista_materias_primas.get(seleccion_indices[0])
            mp_id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            materias_primas_cargadas = listar_materias_primas()
            mp_encontrada = None
            for mp in materias_primas_cargadas:
                if mp.id.startswith(mp_id_abrev):
                    mp_encontrada = mp
                    break

            if mp_encontrada:
                unidad_medida_seleccionada_mp.set(mp_encontrada.unidad_medida)
                unidad_medida_ingresada.set(mp_encontrada.unidad_medida)
                if mp_encontrada.unidad_medida in ("g", "kg"):
                    combo_unidad_ingresada.config(values=["g", "kg"], state="readonly")
                else:
                    combo_unidad_ingresada.config(values=[mp_encontrada.unidad_medida], state="readonly")
            else:
                unidad_medida_seleccionada_mp.set("")
                unidad_medida_ingresada.set("")
        except Exception as e:
            unidad_medida_seleccionada_mp.set("")
            unidad_medida_ingresada.set("")
            # print(f"DEBUG: Error al seleccionar materia prima para unidad de medida: {e}") # Comentado para producción

    def convertir_unidad(cantidad, unidad_origen, unidad_destino):
        conversiones = {
            ("g", "kg"): 0.001,
            ("kg", "g"): 1000,
        }
        if unidad_origen == unidad_destino:
            return cantidad
        factor = conversiones.get((unidad_origen, unidad_destino))
        if factor is None:
            raise ValueError("Conversión de unidades no soportada.")
        return cantidad * factor

    def sincronizar_ingredientes_con_materias_primas():
        """
        Actualiza unidad de medida y costo unitario de ingredientes según materias primas actuales.
        """
        if not ingredientes_receta_actual:
            return
        materias_primas = {mp.id: mp for mp in listar_materias_primas()}
        actualizados = []
        for item in ingredientes_receta_actual:
            mp = materias_primas.get(item["materia_prima_id"])
            if not mp:
                actualizados.append(item)
                continue
            unidad_anterior = item.get("unidad_medida", mp.unidad_medida)
            if unidad_anterior != mp.unidad_medida:
                try:
                    item["cantidad_necesaria"] = convertir_unidad(
                        item["cantidad_necesaria"],
                        unidad_anterior,
                        mp.unidad_medida,
                    )
                except ValueError:
                    pass
            item["unidad_medida"] = mp.unidad_medida
            item["costo_unitario"] = mp.costo_unitario
            actualizados.append(item)
        ingredientes_receta_actual.clear()
        ingredientes_receta_actual.extend(actualizados)

    def cargar_ingrediente_para_editar(event=None):
        nonlocal ultimo_ingrediente_seleccionado
        try:
            seleccion_indices = lista_receta_ingredientes.curselection()
            if not seleccion_indices:
                return
            idx = seleccion_indices[0]
            if idx >= len(ingredientes_receta_actual):
                return
            ultimo_ingrediente_seleccionado = idx
            item = ingredientes_receta_actual[idx]
            entry_cantidad_necesaria.delete(0, tk.END)
            entry_cantidad_necesaria.insert(0, str(item["cantidad_necesaria"]))
            unidad_actual = item.get("unidad_medida", "")
            unidad_medida_ingresada.set(unidad_actual)
            if unidad_actual in ("g", "kg"):
                combo_unidad_ingresada.config(values=["g", "kg"], state="readonly")
            elif unidad_actual:
                combo_unidad_ingresada.config(values=[unidad_actual], state="readonly")
        except Exception:
            return

    def agregar_ingrediente():
        try:
            if not producto_seleccionado_id.get():
                messagebox.showwarning("Atención",
                                       "Primero seleccione un producto para el cual desea crear/editar una receta.")
                return

            seleccion_indices = lista_materias_primas.curselection()
            if not seleccion_indices:
                messagebox.showwarning("Atención", "Seleccione una materia prima de la lista disponible.")
                return

            linea_seleccionada = lista_materias_primas.get(seleccion_indices[0])
            mp_id_abrev = linea_seleccionada.split(' ')[1].replace('...', '')

            materias_primas_cargadas = listar_materias_primas()
            mp_encontrada = None
            for mp in materias_primas_cargadas:
                if mp.id.startswith(mp_id_abrev):
                    mp_encontrada = mp
                    break

            if not mp_encontrada:
                messagebox.showerror("Error", "No se pudo encontrar la materia prima original.")
                return

            cantidad_str = entry_cantidad_necesaria.get()
            try:
                cantidad = float(cantidad_str)
                if cantidad <= 0:
                    messagebox.showerror("Error de Entrada", "La cantidad necesaria debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error de Entrada", "La cantidad necesaria debe ser un número válido.")
                return

            unidad_ingresada = unidad_medida_ingresada.get().strip() or mp_encontrada.unidad_medida
            if unidad_ingresada not in ("g", "kg") and unidad_ingresada != mp_encontrada.unidad_medida:
                unidad_ingresada = mp_encontrada.unidad_medida
            if unidad_ingresada in ("g", "kg") and mp_encontrada.unidad_medida in ("g", "kg"):
                cantidad = convertir_unidad(cantidad, unidad_ingresada, mp_encontrada.unidad_medida)

            for item in ingredientes_receta_actual:
                if item["materia_prima_id"] == mp_encontrada.id:
                    messagebox.showwarning("Duplicado",
                                           "Esta materia prima ya está en la receta. Edite la cantidad existente si desea cambiarla.")
                    return

            ingredientes_receta_actual.append({
                "materia_prima_id": mp_encontrada.id,
                "nombre_materia_prima": mp_encontrada.nombre,
                "cantidad_necesaria": cantidad,
                "unidad_medida": mp_encontrada.unidad_medida,
                "costo_unitario": mp_encontrada.costo_unitario  # Añadir el costo unitario aquí
            })
            actualizar_lista_receta_ingredientes()
            entry_cantidad_necesaria.delete(0, tk.END)
            unidad_medida_seleccionada_mp.set("")  # Limpiar la unidad de medida
            unidad_medida_ingresada.set("")
            messagebox.showinfo("Añadido", f"'{mp_encontrada.nombre}' añadido a la receta.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al añadir ingrediente: {e}")

    def actualizar_cantidad_ingrediente():
        nonlocal ultimo_ingrediente_seleccionado
        try:
            seleccion_indices = lista_receta_ingredientes.curselection()
            if not seleccion_indices and ultimo_ingrediente_seleccionado is not None:
                seleccion_indices = (ultimo_ingrediente_seleccionado,)
            if not seleccion_indices:
                messagebox.showwarning("Atención", "Seleccione un ingrediente de la receta para actualizar.")
                return

            idx = seleccion_indices[0]
            if idx >= len(ingredientes_receta_actual):
                messagebox.showwarning("Atención", "Seleccione un ingrediente válido para actualizar.")
                return
            ultimo_ingrediente_seleccionado = idx

            item = ingredientes_receta_actual[idx]
            mp = obtener_materia_prima_por_id(item["materia_prima_id"])
            if not mp:
                messagebox.showerror("Error", "No se pudo encontrar la materia prima asociada.")
                return

            cantidad_str = entry_cantidad_necesaria.get()
            try:
                cantidad = float(cantidad_str)
                if cantidad <= 0:
                    messagebox.showerror("Error de Entrada", "La cantidad necesaria debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error de Entrada", "La cantidad necesaria debe ser un número válido.")
                return

            unidad_ingresada = unidad_medida_ingresada.get().strip() or mp.unidad_medida
            if unidad_ingresada not in ("g", "kg") and unidad_ingresada != mp.unidad_medida:
                unidad_ingresada = mp.unidad_medida
            if unidad_ingresada in ("g", "kg") and mp.unidad_medida in ("g", "kg"):
                cantidad = convertir_unidad(cantidad, unidad_ingresada, mp.unidad_medida)

            item["cantidad_necesaria"] = cantidad
            item["unidad_medida"] = mp.unidad_medida
            item["costo_unitario"] = mp.costo_unitario
            actualizar_lista_receta_ingredientes()
            messagebox.showinfo("Actualizado", f"Cantidad de '{item['nombre_materia_prima']}' actualizada.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al actualizar cantidad: {e}")

    def eliminar_ingrediente():
        try:
            seleccion_indices = lista_receta_ingredientes.curselection()
            if not seleccion_indices:
                messagebox.showwarning("Atención", "Seleccione un ingrediente de la receta para eliminar.")
                return

            idx_a_eliminar = seleccion_indices[0]
            # Asegurarse de no eliminar las líneas de resumen de costo
            if idx_a_eliminar >= len(ingredientes_receta_actual):
                messagebox.showwarning("Atención", "Seleccione un ingrediente válido para eliminar.")
                return

            nombre_ingrediente = ingredientes_receta_actual[idx_a_eliminar]['nombre_materia_prima']

            confirmar = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar '{nombre_ingrediente}' de la receta?"
            )
            if confirmar:
                del ingredientes_receta_actual[idx_a_eliminar]
                actualizar_lista_receta_ingredientes()
                messagebox.showinfo("Eliminado", f"'{nombre_ingrediente}' eliminado de la receta.")
            else:
                messagebox.showinfo("Cancelado", "Eliminación de ingrediente cancelada.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar ingrediente: {e}")

    def limpiar_receta_actual():
        """
        Limpia la receta actual en la interfaz y en las variables de control.
        """
        confirmar = messagebox.askyesno(
            "Confirmar Limpieza",
            "¿Está seguro de que desea limpiar todos los ingredientes de la receta actual? Esto no guarda los cambios."
        )
        if confirmar:
            producto_seleccionado_id.set("")
            receta_actual_id.set("")
            ingredientes_receta_actual.clear()
            rendimiento_var.set("1")  # Resetear rendimiento
            actualizar_lista_receta_ingredientes()
            entry_buscar_producto.delete(0, tk.END)
            entry_buscar_mp.delete(0, tk.END)
            entry_cantidad_necesaria.delete(0, tk.END)
            unidad_medida_seleccionada_mp.set("")  # Limpiar la unidad de medida
            unidad_medida_ingresada.set("")
            text_procedimiento.delete("1.0", tk.END)
            cargar_productos_en_lista(filtro_texto="", filtro_tipo=filtro_receta_var.get())
            messagebox.showinfo("Receta Limpiada", "La receta actual ha sido limpiada.")
        else:
            messagebox.showinfo("Cancelado", "Limpieza de receta cancelada.")

    def guardar_receta():
        prod_id = producto_seleccionado_id.get()
        if not prod_id:
            messagebox.showwarning("Atención", "Seleccione un producto para guardar la receta.")
            return

        if not ingredientes_receta_actual:
            messagebox.showwarning("Atención", "Una receta debe tener al menos un ingrediente.")
            return

        producto = obtener_producto_por_id(prod_id)
        if not producto:
            messagebox.showerror("Error", "Producto asociado a la receta no encontrado.")
            return
        nombre_prod = producto.nombre

        # Obtener el rendimiento
        try:
            rendimiento = float(rendimiento_var.get())
            if rendimiento <= 0:
                messagebox.showerror("Error de Validación", "El rendimiento debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error de Validación", "El rendimiento debe ser un número válido.")
            return

        procedimiento = text_procedimiento.get("1.0", tk.END).strip()
        if not procedimiento:
            procedimiento = None

        sincronizar_ingredientes_con_materias_primas()
        ingredientes_para_guardar = [
            {k: v for k, v in item.items() if k != 'costo_unitario'}
            for item in ingredientes_receta_actual
        ]

        es_valido, mensaje_error = validar_receta_completa(
            ingredientes_para_guardar, rendimiento, procedimiento
        )
        if not es_valido:
            messagebox.showerror("Error de Validación de Receta", mensaje_error)
            return

        try:

            if receta_actual_id.get():
                editar_receta(
                    receta_actual_id.get(),
                    ingredientes_para_guardar,
                    rendimiento,
                    procedimiento,
                )
                messagebox.showinfo("Éxito", f"Receta para '{nombre_prod}' actualizada correctamente.")
            else:
                agregar_receta(
                    prod_id,
                    nombre_prod,
                    ingredientes_para_guardar,
                    rendimiento,
                    procedimiento,
                )
                messagebox.showinfo("Éxito", f"Receta para '{nombre_prod}' creada correctamente.")

            producto_seleccionado_id.set("")
            receta_actual_id.set("")
            ingredientes_receta_actual.clear()
            rendimiento_var.set("1")  # Resetear rendimiento
            actualizar_lista_receta_ingredientes()
            cargar_productos_en_lista(filtro_texto=entry_buscar_producto.get(), filtro_tipo=filtro_receta_var.get())
            entry_buscar_producto.delete(0, tk.END)
            entry_buscar_mp.delete(0, tk.END)
            entry_cantidad_necesaria.delete(0, tk.END)
            unidad_medida_seleccionada_mp.set("")  # Limpiar la unidad de medida
            unidad_medida_ingresada.set("")
            text_procedimiento.delete("1.0", tk.END)

        except ValueError as e:
            messagebox.showerror("Error al Guardar Receta", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al guardar la receta: {e}")

    def eliminar_receta_seleccionada():
        prod_id = producto_seleccionado_id.get()
        rec_id = receta_actual_id.get()
        if not prod_id or not rec_id:
            messagebox.showwarning("Atención", "Seleccione un producto con una receta cargada para eliminarla.")
            return

        producto = obtener_producto_por_id(prod_id)
        nombre_prod = producto.nombre if producto else "Producto Desconocido"

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación de Receta",
            f"¿Está seguro de que desea eliminar la receta para '{nombre_prod}'? Esta acción no se puede deshacer."
        )
        if confirmar:
            try:
                eliminar_receta(rec_id)
                messagebox.showinfo("Éxito", f"Receta para '{nombre_prod}' eliminada correctamente.")
                producto_seleccionado_id.set("")
                receta_actual_id.set("")
                ingredientes_receta_actual.clear()
                rendimiento_var.set("1")  # Resetear rendimiento
                actualizar_lista_receta_ingredientes()
                cargar_productos_en_lista(filtro_texto=entry_buscar_producto.get(), filtro_tipo=filtro_receta_var.get())
                entry_buscar_producto.delete(0, tk.END)
                entry_buscar_mp.delete(0, tk.END)
                entry_cantidad_necesaria.delete(0, tk.END)
                unidad_medida_seleccionada_mp.set("")  # Limpiar la unidad de medida
            except ValueError as e:
                messagebox.showerror("Error al Eliminar Receta", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Eliminación de receta cancelada.")

    def on_filtro_receta_cambiado_trace(*args):
        current_text_filter = entry_buscar_producto.get()
        current_recipe_filter = filtro_receta_var.get()
        cargar_productos_en_lista(filtro_texto=current_text_filter, filtro_tipo=current_recipe_filter)

    # --- Widgets de la Interfaz ---

    tk.Label(ventana, text="Gestión de Recetas", font=("Helvetica", 18, "bold")).pack(pady=10)
    tk.Label(ventana, text="Seleccione un producto, añada los ingredientes necesarios y guarde la receta.",
             font=("Helvetica", 10)).pack(pady=5)

    # --- Sección de Selección de Producto ---
    frame_productos = tk.LabelFrame(ventana, text="1. Seleccionar Producto para Receta", padx=10, pady=10)
    frame_productos.pack(pady=5, fill=tk.X, padx=10)

    tk.Label(frame_productos, text="Buscar Producto:").pack(side=tk.LEFT, padx=5)
    entry_buscar_producto = tk.Entry(frame_productos, width=30)
    entry_buscar_producto.pack(side=tk.LEFT, padx=5)

    tk.Label(frame_productos, text="Filtrar por Receta:").pack(side=tk.LEFT, padx=(15, 5))
    combobox_filtro_receta = ttk.Combobox(frame_productos, textvariable=filtro_receta_var,
                                          values=["Todos", "Sin Receta", "Con Receta"], state="readonly", width=15)
    combobox_filtro_receta.pack(side=tk.LEFT, padx=5)
    combobox_filtro_receta.set("Todos")  # Valor por defecto

    scrollbar_productos = tk.Scrollbar(frame_productos, orient=tk.VERTICAL)
    lista_productos = tk.Listbox(frame_productos, height=5, width=60, yscrollcommand=scrollbar_productos.set,
                                 exportselection=False)
    scrollbar_productos.config(command=lista_productos.yview)
    scrollbar_productos.pack(side=tk.RIGHT, fill=tk.Y)
    lista_productos.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    # --- Sección de Ingredientes de la Receta ---
    frame_ingredientes_receta = tk.LabelFrame(ventana, text="2. Ingredientes de la Receta Actual", padx=10, pady=10)
    frame_ingredientes_receta.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)

    # Nuevo: Campo para el rendimiento
    tk.Label(frame_ingredientes_receta, text="Rendimiento de la Receta (unidades):").pack(pady=(0, 5))
    entry_rendimiento = tk.Entry(frame_ingredientes_receta, textvariable=rendimiento_var, width=10)
    entry_rendimiento.pack(pady=(0, 10))
    entry_rendimiento.bind("<KeyRelease>",
                           lambda event: actualizar_lista_receta_ingredientes())  # Actualizar al cambiar rendimiento

    scrollbar_receta_ingredientes = tk.Scrollbar(frame_ingredientes_receta, orient=tk.VERTICAL)
    lista_receta_ingredientes = tk.Listbox(
        frame_ingredientes_receta,
        height=8,
        width=70,
        yscrollcommand=scrollbar_receta_ingredientes.set,
        exportselection=False,
    )
    scrollbar_receta_ingredientes.config(command=lista_receta_ingredientes.yview)
    scrollbar_receta_ingredientes.pack(side=tk.RIGHT, fill=tk.Y)
    lista_receta_ingredientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    tk.Label(frame_ingredientes_receta, text="Procedimiento:").pack(pady=(10, 0), anchor="w")
    text_procedimiento = tk.Text(frame_ingredientes_receta, height=5, width=70)
    text_procedimiento.pack(fill=tk.BOTH, padx=5, pady=(0, 10))

    def abrir_editor_procedimiento():
        editor = tk.Toplevel(ventana)
        editor.title("Editar procedimiento")
        text_editor = tk.Text(editor, height=20, width=80)
        text_editor.pack(padx=10, pady=10)
        text_editor.insert("1.0", text_procedimiento.get("1.0", tk.END))

        def guardar():
            text_procedimiento.delete("1.0", tk.END)
            text_procedimiento.insert("1.0", text_editor.get("1.0", tk.END))
            editor.destroy()

        tk.Button(editor, text="Guardar", command=guardar).pack(pady=5)

    tk.Button(frame_ingredientes_receta, text="Editar en ventana…", command=abrir_editor_procedimiento).pack(pady=(0, 10))

    tk.Button(
        frame_ingredientes_receta,
        text="Eliminar Ingrediente Seleccionado",
        command=eliminar_ingrediente,
        width=30,
    ).pack(pady=5)
    tk.Button(
        frame_ingredientes_receta,
        text="Limpiar Receta Actual",
        command=limpiar_receta_actual,
        width=30,
    ).pack(pady=5)

    # --- Sección de Añadir Materia Prima a Receta ---
    frame_add_mp = tk.LabelFrame(ventana, text="3. Añadir Materia Prima a Receta", padx=10, pady=10)
    frame_add_mp.pack(pady=5, fill=tk.X, padx=10)

    tk.Label(frame_add_mp, text="Buscar Materia Prima:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_buscar_mp = tk.Entry(frame_add_mp, width=30)
    entry_buscar_mp.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    scrollbar_mp = tk.Scrollbar(frame_add_mp, orient=tk.VERTICAL)
    lista_materias_primas = tk.Listbox(frame_add_mp, height=5, width=60, yscrollcommand=scrollbar_mp.set,
                                       exportselection=False)
    scrollbar_mp.config(command=lista_materias_primas.yview)
    scrollbar_mp.grid(row=0, column=3, rowspan=3, sticky="ns")
    lista_materias_primas.grid(row=0, column=2, rowspan=3, padx=5, pady=2, sticky="nsew")

    tk.Label(frame_add_mp, text="Cantidad Necesaria:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_cantidad_necesaria = tk.Entry(frame_add_mp, width=15)
    entry_cantidad_necesaria.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
    combo_unidad_ingresada = ttk.Combobox(
        frame_add_mp,
        textvariable=unidad_medida_ingresada,
        values=["g", "kg"],
        state="readonly",
        width=5,
    )
    combo_unidad_ingresada.grid(row=1, column=1, padx=(70, 0), pady=2, sticky="e")
    label_unidad_medida = tk.Label(frame_add_mp, textvariable=unidad_medida_seleccionada_mp,
                                   font=("Helvetica", 9, "italic"))
    label_unidad_medida.grid(row=1, column=1, padx=(120, 0), pady=2, sticky="e")  # Posicionar a la derecha del entry

    # Configurar el grid para que la columna 2 (lista_materias_primas) se expanda
    frame_add_mp.grid_columnconfigure(2, weight=1)

    # --- Botones ---
    tk.Button(frame_add_mp, text="Añadir Ingrediente", command=agregar_ingrediente, width=20).grid(
        row=2, column=0, columnspan=2, pady=5
    )
    tk.Button(frame_add_mp, text="Actualizar Cantidad", command=actualizar_cantidad_ingrediente, width=20).grid(
        row=2, column=2, pady=5
    )

    tk.Button(ventana, text="Guardar Receta", command=guardar_receta, width=25, bg="lightblue").pack(pady=10)
    tk.Button(ventana, text="Eliminar Receta del Producto", command=eliminar_receta_seleccionada, width=25,
              bg="lightcoral").pack(pady=5)

    # --- Vinculación de Eventos y Carga Inicial ---
    entry_buscar_producto.bind("<KeyRelease>",
                               lambda event: cargar_productos_en_lista(filtro_texto=entry_buscar_producto.get(),
                                                                       filtro_tipo=filtro_receta_var.get()))
    filtro_receta_var.trace_add('write', on_filtro_receta_cambiado_trace)
    lista_productos.bind("<<ListboxSelect>>", on_producto_seleccionado)
    entry_buscar_mp.bind("<KeyRelease>", lambda event: cargar_materias_primas_en_lista(entry_buscar_mp.get()))
    lista_materias_primas.bind("<<ListboxSelect>>",
                               on_materia_prima_seleccionada)  # Nuevo bind para actualizar la unidad de medida
    lista_receta_ingredientes.bind("<<ListboxSelect>>", cargar_ingrediente_para_editar)

    cargar_productos_en_lista()
    cargar_materias_primas_en_lista()
    actualizar_lista_receta_ingredientes()
