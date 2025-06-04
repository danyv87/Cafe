import tkinter as tk
from tkinter import ttk # Importar ttk para mejores widgets, como Treeview y Notebook
from controllers.tickets_controller import obtener_ventas_por_mes, obtener_ventas_por_semana # Importa ambas funciones

def mostrar_ventana_estadisticas():
    ventana = tk.Toplevel()
    ventana.title("Estadísticas de Ventas")
    ventana.geometry("650x550") # Ajusta el tamaño para acomodar las pestañas y tablas

    tk.Label(ventana, text="Estadísticas de Ventas", font=("Helvetica", 16, "bold")).pack(pady=10)

    # Crear un Notebook (widget de pestañas)
    notebook = ttk.Notebook(ventana)
    notebook.pack(pady=10, fill=tk.BOTH, expand=True)

    # --- Pestaña de Estadísticas Mensuales ---
    frame_mensual = ttk.Frame(notebook)
    notebook.add(frame_mensual, text="Por Mes")

    tk.Label(frame_mensual, text="Ventas Agrupadas por Mes", font=("Helvetica", 12, "bold")).pack(pady=5)

    tree_mensual = ttk.Treeview(frame_mensual, columns=("Mes", "Total Vendido"), show="headings", height=15)
    tree_mensual.heading("Mes", text="Mes (YYYY-MM)")
    tree_mensual.heading("Total Vendido", text="Total Vendido (Gs)")

    tree_mensual.column("Mes", width=150, anchor="center")
    tree_mensual.column("Total Vendido", width=200, anchor="e")

    tree_mensual.pack(pady=5, fill=tk.BOTH, expand=True)

    # Obtener los datos de ventas por mes
    ventas_por_mes = obtener_ventas_por_mes()

    if not ventas_por_mes:
        tree_mensual.insert("", tk.END, values=("No hay datos de ventas mensuales para mostrar.", ""))
    else:
        for mes_año, total in ventas_por_mes:
            tree_mensual.insert("", tk.END, values=(mes_año, total)) # 'total' ya viene formateado

    # Añadir un scrollbar al Treeview mensual
    scrollbar_mensual = ttk.Scrollbar(frame_mensual, orient=tk.VERTICAL, command=tree_mensual.yview)
    tree_mensual.configure(yscrollcommand=scrollbar_mensual.set)
    scrollbar_mensual.pack(side=tk.RIGHT, fill=tk.Y)
    tree_mensual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    # --- Pestaña de Estadísticas Semanales ---
    frame_semanal = ttk.Frame(notebook)
    notebook.add(frame_semanal, text="Por Semana")

    tk.Label(frame_semanal, text="Ventas Agrupadas por Semana", font=("Helvetica", 12, "bold")).pack(pady=5)

    tree_semanal = ttk.Treeview(frame_semanal, columns=("Semana", "Total Vendido"), show="headings", height=15)
    tree_semanal.heading("Semana", text="Semana (YYYY-WNN)")
    tree_semanal.heading("Total Vendido", text="Total Vendido (Gs)")

    tree_semanal.column("Semana", width=150, anchor="center")
    tree_semanal.column("Total Vendido", width=200, anchor="e")

    tree_semanal.pack(pady=5, fill=tk.BOTH, expand=True)

    # Obtener los datos de ventas por semana
    ventas_por_semana = obtener_ventas_por_semana()

    if not ventas_por_semana:
        tree_semanal.insert("", tk.END, values=("No hay datos de ventas semanales para mostrar.", ""))
    else:
        for semana_año, total in ventas_por_semana:
            tree_semanal.insert("", tk.END, values=(semana_año, total)) # 'total' ya viene formateado

    # Añadir un scrollbar al Treeview semanal
    scrollbar_semanal = ttk.Scrollbar(frame_semanal, orient=tk.VERTICAL, command=tree_semanal.yview)
    tree_semanal.configure(yscrollcommand=scrollbar_semanal.set)
    scrollbar_semanal.pack(side=tk.RIGHT, fill=tk.Y)
    tree_semanal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Establecer la pestaña mensual como la predeterminada al abrir
    notebook.select(frame_mensual)
