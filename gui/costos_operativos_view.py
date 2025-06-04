import tkinter as tk
from tkinter import ttk
from controllers.compras_controller import obtener_compras_por_mes, obtener_compras_por_semana
from controllers.gastos_adicionales_controller import obtener_gastos_adicionales_por_mes, \
    obtener_gastos_adicionales_por_semana
from controllers.tickets_controller import obtener_ventas_por_mes, obtener_ventas_por_semana  # Para mostrar ingresos


def mostrar_ventana_costos_operativos():
    ventana = tk.Toplevel()
    ventana.title("Análisis de Costos Operativos")
    ventana.geometry("900x600")

    tk.Label(ventana, text="Análisis de Costos Operativos", font=("Helvetica", 16, "bold")).pack(pady=15)

    # Crear un Notebook (pestañas) para las vistas mensuales y semanales
    notebook = ttk.Notebook(ventana)
    notebook.pack(pady=10, fill=tk.BOTH, expand=True)

    # --- Pestaña Mensual ---
    frame_mensual = ttk.Frame(notebook)
    notebook.add(frame_mensual, text="Mensual")

    tree_mensual = ttk.Treeview(frame_mensual, columns=(
    "Periodo", "Ingresos", "Costo MP", "Gastos Adicionales", "Costo Total", "Ganancia/Pérdida"), show="headings",
                                height=15)

    tree_mensual.heading("Periodo", text="Periodo (YYYY-MM)")
    tree_mensual.heading("Ingresos", text="Ingresos (Gs)")
    tree_mensual.heading("Costo MP", text="Costo Materias Primas (Gs)")
    tree_mensual.heading("Gastos Adicionales", text="Gastos Adicionales (Gs)")
    tree_mensual.heading("Costo Total", text="Costo Operativo Total (Gs)")
    tree_mensual.heading("Ganancia/Pérdida", text="Ganancia/Pérdida (Gs)")

    tree_mensual.column("Periodo", width=120, anchor="center")
    tree_mensual.column("Ingresos", width=120, anchor="e")
    tree_mensual.column("Costo MP", width=150, anchor="e")
    tree_mensual.column("Gastos Adicionales", width=150, anchor="e")
    tree_mensual.column("Costo Total", width=150, anchor="e")
    tree_mensual.column("Ganancia/Pérdida", width=150, anchor="e")

    tree_mensual.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar_mensual = ttk.Scrollbar(frame_mensual, orient=tk.VERTICAL, command=tree_mensual.yview)
    tree_mensual.configure(yscrollcommand=scrollbar_mensual.set)
    scrollbar_mensual.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Pestaña Semanal ---
    frame_semanal = ttk.Frame(notebook)
    notebook.add(frame_semanal, text="Semanal")

    tree_semanal = ttk.Treeview(frame_semanal, columns=(
    "Periodo", "Ingresos", "Costo MP", "Gastos Adicionales", "Costo Total", "Ganancia/Pérdida"), show="headings",
                                height=15)

    tree_semanal.heading("Periodo", text="Periodo (YYYY-WNN)")
    tree_semanal.heading("Ingresos", text="Ingresos (Gs)")
    tree_semanal.heading("Costo MP", text="Costo Materias Primas (Gs)")
    tree_semanal.heading("Gastos Adicionales", text="Gastos Adicionales (Gs)")
    tree_semanal.heading("Costo Total", text="Costo Operativo Total (Gs)")
    tree_semanal.heading("Ganancia/Pérdida", text="Ganancia/Pérdida (Gs)")

    tree_semanal.column("Periodo", width=120, anchor="center")
    tree_semanal.column("Ingresos", width=120, anchor="e")
    tree_semanal.column("Costo MP", width=150, anchor="e")
    tree_semanal.column("Gastos Adicionales", width=150, anchor="e")
    tree_semanal.column("Costo Total", width=150, anchor="e")
    tree_semanal.column("Ganancia/Pérdida", width=150, anchor="e")

    tree_semanal.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar_semanal = ttk.Scrollbar(frame_semanal, orient=tk.VERTICAL, command=tree_semanal.yview)
    tree_semanal.configure(yscrollcommand=scrollbar_semanal.set)
    scrollbar_semanal.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Funciones de Carga de Datos ---

    def parse_formatted_currency(value_str):
        """Convierte un string de moneda formateado (ej. 'Gs 123.456') a un float."""
        if isinstance(value_str, (int, float)):  # Ya es un número
            return value_str
        try:
            # Eliminar "Gs ", reemplazar puntos por nada y comas por puntos para float
            return float(value_str.replace("Gs ", "").replace(".", "").replace(",", "."))
        except ValueError:
            return 0.0  # En caso de error de parseo

    def format_currency(value):
        """Formatea un número a string de moneda 'Gs X.XXX.XXX,XX'."""
        if isinstance(value, str):  # Si ya es un string formateado, no lo reformateamos
            return value
        return f"Gs {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def cargar_datos_mensuales():
        ventas_mes = dict(obtener_ventas_por_mes())
        compras_mes = dict(obtener_compras_por_mes())
        gastos_adicionales_mes = dict(obtener_gastos_adicionales_por_mes())

        # Obtener todos los meses únicos presentes en cualquiera de las categorías
        all_months = sorted(list(set(ventas_mes.keys()) | set(compras_mes.keys()) | set(gastos_adicionales_mes.keys())))

        tree_mensual.delete(*tree_mensual.get_children())  # Limpiar tabla

        if not all_months:
            tree_mensual.insert("", tk.END, values=("No hay datos para mostrar.", "", "", "", "", ""),
                                tags=('no_data',))
            tree_mensual.tag_configure('no_data', foreground='gray')
            return

        for mes in all_months:
            ingresos_str = ventas_mes.get(mes, "Gs 0")
            costo_mp_str = compras_mes.get(mes, "Gs 0")
            gastos_ad_str = gastos_adicionales_mes.get(mes, "Gs 0")

            ingresos_val = parse_formatted_currency(ingresos_str)
            costo_mp_val = parse_formatted_currency(costo_mp_str)
            gastos_ad_val = parse_formatted_currency(gastos_ad_str)

            costo_total_val = costo_mp_val + gastos_ad_val
            ganancia_perdida_val = ingresos_val - costo_total_val

            # Determinar el color de la fila
            row_tag = 'positive' if ganancia_perdida_val >= 0 else 'negative'

            tree_mensual.insert("", tk.END, values=(
                mes,
                format_currency(ingresos_val),
                format_currency(costo_mp_val),
                format_currency(gastos_ad_val),
                format_currency(costo_total_val),
                format_currency(ganancia_perdida_val)
            ), tags=(row_tag,))

        # Configurar colores para las filas
        tree_mensual.tag_configure('positive', foreground='green')
        tree_mensual.tag_configure('negative', foreground='red')

    def cargar_datos_semanales():
        ventas_semana = dict(obtener_ventas_por_semana())
        compras_semana = dict(obtener_compras_por_semana())
        gastos_adicionales_semana = dict(obtener_gastos_adicionales_por_semana())

        all_weeks = sorted(
            list(set(ventas_semana.keys()) | set(compras_semana.keys()) | set(gastos_adicionales_semana.keys())))

        tree_semanal.delete(*tree_semanal.get_children())  # Limpiar tabla

        if not all_weeks:
            tree_semanal.insert("", tk.END, values=("No hay datos para mostrar.", "", "", "", "", ""),
                                tags=('no_data',))
            tree_semanal.tag_configure('no_data', foreground='gray')
            return

        for semana in all_weeks:
            ingresos_str = ventas_semana.get(semana, "Gs 0")
            costo_mp_str = compras_semana.get(semana, "Gs 0")
            gastos_ad_str = gastos_adicionales_semana.get(semana, "Gs 0")

            ingresos_val = parse_formatted_currency(ingresos_str)
            costo_mp_val = parse_formatted_currency(costo_mp_str)
            gastos_ad_val = parse_formatted_currency(gastos_ad_str)

            costo_total_val = costo_mp_val + gastos_ad_val
            ganancia_perdida_val = ingresos_val - costo_total_val

            row_tag = 'positive' if ganancia_perdida_val >= 0 else 'negative'

            tree_semanal.insert("", tk.END, values=(
                semana,
                format_currency(ingresos_val),
                format_currency(costo_mp_val),
                format_currency(gastos_ad_val),
                format_currency(costo_total_val),
                format_currency(ganancia_perdida_val)
            ), tags=(row_tag,))

        tree_semanal.tag_configure('positive', foreground='green')
        tree_semanal.tag_configure('negative', foreground='red')

    # Cargar datos al seleccionar la pestaña
    def on_tab_selected(event):
        selected_tab = notebook.tab(notebook.select(), "text")
        if selected_tab == "Mensual":
            cargar_datos_mensuales()
        elif selected_tab == "Semanal":
            cargar_datos_semanales()

    notebook.bind("<<NotebookTabChanged>>", on_tab_selected)

    # Cargar datos iniciales (para la pestaña por defecto)
    cargar_datos_mensuales()

