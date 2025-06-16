import tkinter as tk
from tkinter import ttk
from controllers.compras_controller import (
    obtener_compras_por_mes,
    obtener_compras_por_semana,
    obtener_compras_por_dia
)
from controllers.gastos_adicionales_controller import (
    obtener_gastos_adicionales_por_mes,
    obtener_gastos_adicionales_por_semana,
    obtener_gastos_adicionales_por_dia
)
from controllers.tickets_controller import (
    obtener_ventas_por_mes,
    obtener_ventas_por_semana,
    obtener_ventas_por_dia
)

def mostrar_ventana_costos_operativos():
    ventana = tk.Toplevel()
    ventana.title("Análisis de Costos Operativos")
    ventana.geometry("900x600")

    tk.Label(ventana, text="Análisis de Costos Operativos", font=("Helvetica", 16, "bold")).pack(pady=15)

    # Crear un Notebook (pestañas) para las vistas mensuales, semanales y diarias
    notebook = ttk.Notebook(ventana)
    notebook.pack(pady=10, fill=tk.BOTH, expand=True)

    # --- Pestaña Mensual ---
    frame_mensual = ttk.Frame(notebook)
    notebook.add(frame_mensual, text="Mensual")

    tree_mensual = ttk.Treeview(
        frame_mensual,
        columns=("Periodo", "Ingresos", "Costo MP", "Gastos Adicionales", "Costo Total", "Ganancia/Pérdida"),
        show="headings",
        height=15
    )

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

    tree_semanal = ttk.Treeview(
        frame_semanal,
        columns=("Periodo", "Ingresos", "Costo MP", "Gastos Adicionales", "Costo Total", "Ganancia/Pérdida"),
        show="headings",
        height=15
    )

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

    # --- Pestaña Diaria ---
    frame_diario = ttk.Frame(notebook)
    notebook.add(frame_diario, text="Diario")

    tree_diario = ttk.Treeview(
        frame_diario,
        columns=("Periodo", "Ingresos", "Costo MP", "Gastos Adicionales", "Costo Total", "Ganancia/Pérdida"),
        show="headings",
        height=15
    )

    tree_diario.heading("Periodo", text="Periodo (YYYY-MM-DD)")
    tree_diario.heading("Ingresos", text="Ingresos (Gs)")
    tree_diario.heading("Costo MP", text="Costo Materias Primas (Gs)")
    tree_diario.heading("Gastos Adicionales", text="Gastos Adicionales (Gs)")
    tree_diario.heading("Costo Total", text="Costo Operativo Total (Gs)")
    tree_diario.heading("Ganancia/Pérdida", text="Ganancia/Pérdida (Gs)")

    tree_diario.column("Periodo", width=120, anchor="center")
    tree_diario.column("Ingresos", width=120, anchor="e")
    tree_diario.column("Costo MP", width=150, anchor="e")
    tree_diario.column("Gastos Adicionales", width=150, anchor="e")
    tree_diario.column("Costo Total", width=150, anchor="e")
    tree_diario.column("Ganancia/Pérdida", width=150, anchor="e")

    tree_diario.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar_diario = ttk.Scrollbar(frame_diario, orient=tk.VERTICAL, command=tree_diario.yview)
    tree_diario.configure(yscrollcommand=scrollbar_diario.set)
    scrollbar_diario.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Funciones de Carga de Datos ---

    def parse_formatted_currency(value_str):
        if isinstance(value_str, (int, float)):
            return value_str
        try:
            return float(value_str.replace("Gs ", "").replace(".", "").replace(",", "."))
        except ValueError:
            return 0.0

    def format_currency(value):
        if isinstance(value, str):
            return value
        return f"Gs {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def cargar_datos(tree, ventas, compras, gastos_adicionales, periodo_label):
        all_periods = sorted(list(set(ventas.keys()) | set(compras.keys()) | set(gastos_adicionales.keys())))
        tree.delete(*tree.get_children())
        if not all_periods:
            tree.insert("", tk.END, values=("No hay datos para mostrar.", "", "", "", "", ""), tags=('no_data',))
            tree.tag_configure('no_data', foreground='gray')
            return

        for periodo in all_periods:
            ingresos_str = ventas.get(periodo, "Gs 0")
            costo_mp_str = compras.get(periodo, "Gs 0")
            gastos_ad_str = gastos_adicionales.get(periodo, "Gs 0")

            ingresos_val = parse_formatted_currency(ingresos_str)
            costo_mp_val = parse_formatted_currency(costo_mp_str)
            gastos_ad_val = parse_formatted_currency(gastos_ad_str)

            costo_total_val = costo_mp_val + gastos_ad_val
            ganancia_perdida_val = ingresos_val - costo_total_val

            row_tag = 'positive' if ganancia_perdida_val >= 0 else 'negative'

            tree.insert("", tk.END, values=(
                periodo,
                format_currency(ingresos_val),
                format_currency(costo_mp_val),
                format_currency(gastos_ad_val),
                format_currency(costo_total_val),
                format_currency(ganancia_perdida_val)
            ), tags=(row_tag,))

        tree.tag_configure('positive', foreground='green')
        tree.tag_configure('negative', foreground='red')

    def cargar_datos_mensuales():
        ventas_mes = dict(obtener_ventas_por_mes())
        compras_mes = dict(obtener_compras_por_mes())
        gastos_adicionales_mes = dict(obtener_gastos_adicionales_por_mes())
        cargar_datos(tree_mensual, ventas_mes, compras_mes, gastos_adicionales_mes, "Periodo (YYYY-MM)")

    def cargar_datos_semanales():
        ventas_semana = dict(obtener_ventas_por_semana())
        compras_semana = dict(obtener_compras_por_semana())
        gastos_adicionales_semana = dict(obtener_gastos_adicionales_por_semana())
        cargar_datos(tree_semanal, ventas_semana, compras_semana, gastos_adicionales_semana, "Periodo (YYYY-WNN)")

    def cargar_datos_diarios():
        ventas_dia = dict(obtener_ventas_por_dia())
        compras_dia = dict(obtener_compras_por_dia())
        gastos_adicionales_dia = dict(obtener_gastos_adicionales_por_dia())
        cargar_datos(tree_diario, ventas_dia, compras_dia, gastos_adicionales_dia, "Periodo (YYYY-MM-DD)")

    def on_tab_selected(event):
        selected_tab = notebook.tab(notebook.select(), "text")
        if selected_tab == "Mensual":
            cargar_datos_mensuales()
        elif selected_tab == "Semanal":
            cargar_datos_semanales()
        elif selected_tab == "Diario":
            cargar_datos_diarios()

    notebook.bind("<<NotebookTabChanged>>", on_tab_selected)

    # Cargar datos iniciales
    cargar_datos_mensuales()