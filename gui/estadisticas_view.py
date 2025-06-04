import tkinter as tk
from tkinter import ttk  # Importar ttk para mejores widgets, como Treeview y Notebook
from controllers.tickets_controller import obtener_ventas_por_mes, obtener_ventas_por_semana, \
    total_vendido_tickets  # Importa ambas funciones de ventas y el total general
from controllers.compras_controller import obtener_compras_por_mes, obtener_compras_por_semana, \
    total_comprado  # ¡Nuevas importaciones para compras y el total general!


def mostrar_ventana_estadisticas():
    ventana = tk.Toplevel()
    ventana.title("Estadísticas de Ventas y Compras")  # Título actualizado
    ventana.geometry("700x700")  # Ajusta el tamaño para acomodar el balance

    tk.Label(ventana, text="Estadísticas de Ventas y Compras", font=("Helvetica", 16, "bold")).pack(pady=10)

    # Crear un Notebook (widget de pestañas)
    notebook = ttk.Notebook(ventana)
    notebook.pack(pady=10, fill=tk.BOTH, expand=True)

    # --- Pestaña de Estadísticas Mensuales de Ventas ---
    frame_ventas_mensual = ttk.Frame(notebook)
    notebook.add(frame_ventas_mensual, text="Ventas por Mes")

    tk.Label(frame_ventas_mensual, text="Ventas Agrupadas por Mes", font=("Helvetica", 12, "bold")).pack(pady=5)

    tree_ventas_mensual = ttk.Treeview(frame_ventas_mensual, columns=("Mes", "Total Vendido"), show="headings",
                                       height=15)
    tree_ventas_mensual.heading("Mes", text="Mes (YYYY-MM)")
    tree_ventas_mensual.heading("Total Vendido", text="Total Vendido (Gs)")

    tree_ventas_mensual.column("Mes", width=150, anchor="center")
    tree_ventas_mensual.column("Total Vendido", width=200, anchor="e")

    tree_ventas_mensual.pack(pady=5, fill=tk.BOTH, expand=True)

    ventas_por_mes = obtener_ventas_por_mes()
    if not ventas_por_mes:
        tree_ventas_mensual.insert("", tk.END, values=("No hay datos de ventas mensuales para mostrar.", ""))
    else:
        for mes_año, total in ventas_por_mes:
            tree_ventas_mensual.insert("", tk.END, values=(mes_año, total))

    scrollbar_ventas_mensual = ttk.Scrollbar(frame_ventas_mensual, orient=tk.VERTICAL,
                                             command=tree_ventas_mensual.yview)
    tree_ventas_mensual.configure(yscrollcommand=scrollbar_ventas_mensual.set)
    scrollbar_ventas_mensual.pack(side=tk.RIGHT, fill=tk.Y)
    tree_ventas_mensual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # --- Pestaña de Estadísticas Semanales de Ventas ---
    frame_ventas_semanal = ttk.Frame(notebook)
    notebook.add(frame_ventas_semanal, text="Ventas por Semana")

    tk.Label(frame_ventas_semanal, text="Ventas Agrupadas por Semana", font=("Helvetica", 12, "bold")).pack(pady=5)

    tree_ventas_semanal = ttk.Treeview(frame_ventas_semanal, columns=("Semana", "Total Vendido"), show="headings",
                                       height=15)
    tree_ventas_semanal.heading("Semana", text="Semana (YYYY-WNN)")
    tree_ventas_semanal.heading("Total Vendido", text="Total Vendido (Gs)")

    tree_ventas_semanal.column("Semana", width=150, anchor="center")
    tree_ventas_semanal.column("Total Vendido", width=200, anchor="e")

    tree_ventas_semanal.pack(pady=5, fill=tk.BOTH, expand=True)

    ventas_por_semana = obtener_ventas_por_semana()
    if not ventas_por_semana:
        tree_ventas_semanal.insert("", tk.END, values=("No hay datos de ventas semanales para mostrar.", ""))
    else:
        for semana_año, total in ventas_por_semana:
            tree_ventas_semanal.insert("", tk.END, values=(semana_año, total))

    scrollbar_ventas_semanal = ttk.Scrollbar(frame_ventas_semanal, orient=tk.VERTICAL,
                                             command=tree_ventas_semanal.yview)
    tree_ventas_semanal.configure(yscrollcommand=scrollbar_ventas_semanal.set)
    scrollbar_ventas_semanal.pack(side=tk.RIGHT, fill=tk.Y)
    tree_ventas_semanal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # --- Pestaña de Estadísticas Mensuales de Compras ---
    frame_compras_mensual = ttk.Frame(notebook)
    notebook.add(frame_compras_mensual, text="Compras por Mes")

    tk.Label(frame_compras_mensual, text="Compras Agrupadas por Mes", font=("Helvetica", 12, "bold")).pack(pady=5)

    tree_compras_mensual = ttk.Treeview(frame_compras_mensual, columns=("Mes", "Total Comprado"), show="headings",
                                        height=15)
    tree_compras_mensual.heading("Mes", text="Mes (YYYY-MM)")
    tree_compras_mensual.heading("Total Comprado", text="Total Comprado (Gs)")

    tree_compras_mensual.column("Mes", width=150, anchor="center")
    tree_compras_mensual.column("Total Comprado", width=200, anchor="e")

    tree_compras_mensual.pack(pady=5, fill=tk.BOTH, expand=True)

    compras_por_mes = obtener_compras_por_mes()  # Obtener los datos de compras por mes
    if not compras_por_mes:
        tree_compras_mensual.insert("", tk.END, values=("No hay datos de compras mensuales para mostrar.", ""))
    else:
        for mes_año, total in compras_por_mes:
            tree_compras_mensual.insert("", tk.END, values=(mes_año, total))

    scrollbar_compras_mensual = ttk.Scrollbar(frame_compras_mensual, orient=tk.VERTICAL,
                                              command=tree_compras_mensual.yview)
    tree_compras_mensual.configure(yscrollcommand=scrollbar_compras_mensual.set)
    scrollbar_compras_mensual.pack(side=tk.RIGHT, fill=tk.Y)
    tree_compras_mensual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # --- Pestaña de Estadísticas Semanales de Compras ---
    frame_compras_semanal = ttk.Frame(notebook)
    notebook.add(frame_compras_semanal, text="Compras por Semana")

    tk.Label(frame_compras_semanal, text="Compras Agrupadas por Semana", font=("Helvetica", 12, "bold")).pack(pady=5)

    tree_compras_semanal = ttk.Treeview(frame_compras_semanal, columns=("Semana", "Total Comprado"), show="headings",
                                        height=15)
    tree_compras_semanal.heading("Semana", text="Semana (YYYY-WNN)")
    tree_compras_semanal.heading("Total Comprado", text="Total Comprado (Gs)")

    tree_compras_semanal.column("Semana", width=150, anchor="center")
    tree_compras_semanal.column("Total Comprado", width=200, anchor="e")

    tree_compras_semanal.pack(pady=5, fill=tk.BOTH, expand=True)

    compras_por_semana = obtener_compras_por_semana()  # Obtener los datos de compras por semana
    if not compras_por_semana:
        tree_compras_semanal.insert("", tk.END, values=("No hay datos de compras semanales para mostrar.", ""))
    else:
        for semana_año, total in compras_por_semana:
            tree_compras_semanal.insert("", tk.END, values=(semana_año, total))

    scrollbar_compras_semanal = ttk.Scrollbar(frame_compras_semanal, orient=tk.VERTICAL,
                                              command=tree_compras_semanal.yview)
    tree_compras_semanal.configure(yscrollcommand=scrollbar_compras_semanal.set)
    scrollbar_compras_semanal.pack(side=tk.RIGHT, fill=tk.Y)
    tree_compras_semanal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Establecer la pestaña de ventas mensuales como la predeterminada al abrir
    notebook.select(frame_ventas_mensual)

    # --- Sección de Balance General ---
    total_ventas_general = total_vendido_tickets()
    total_compras_general = total_comprado()
    balance_general = total_ventas_general - total_compras_general

    # Formatear el balance con separador de miles y signo de moneda
    balance_formateado = f"{balance_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    color_balance = "green" if balance_general >= 0 else "red"

    tk.Label(ventana, text="--- Balance General ---", font=("Helvetica", 14, "bold")).pack(pady=(15, 5))
    tk.Label(ventana,
             text=f"Total Ventas: Gs {total_ventas_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
             font=("Helvetica", 12)).pack()
    tk.Label(ventana,
             text=f"Total Compras: Gs {total_compras_general:,.0f}".replace(",", "X").replace(".", ",").replace("X",
                                                                                                                "."),
             font=("Helvetica", 12)).pack()
    tk.Label(ventana, text=f"Balance Neto: Gs {balance_formateado}", font=("Helvetica", 14, "bold"),
             fg=color_balance).pack(pady=5)
