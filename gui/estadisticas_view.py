import tkinter as tk
from tkinter import ttk
from controllers.tickets_controller import (
    obtener_ventas_por_mes,
    obtener_ventas_por_semana,
    total_vendido_tickets,
    obtener_ventas_por_producto,
)
from controllers.compras_controller import (
    obtener_compras_por_mes,
    obtener_compras_por_semana,
    total_comprado,
)
from controllers.productos_controller import obtener_producto_por_id
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np


def _formatear_moneda(valor: float) -> str:
    return f"Gs {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def agregar_tab_estadisticas(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña con estadísticas de ventas y compras."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Estadísticas")

    main_canvas = tk.Canvas(frame)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_main = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=main_canvas.yview)
    scrollbar_main.pack(side=tk.RIGHT, fill=tk.Y)

    main_canvas.configure(yscrollcommand=scrollbar_main.set)
    main_canvas.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

    content_frame = tk.Frame(main_canvas)
    main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    tk.Label(content_frame, text="Estadísticas de Ventas y Compras", font=("Helvetica", 18, "bold")).pack(pady=10)

    tk.Label(content_frame, text="Ventas Agrupadas por Mes", font=("Helvetica", 12, "bold")).pack(pady=(15, 5))
    tree_ventas_mensual = ttk.Treeview(content_frame, columns=("Mes", "Total Vendido"), show="headings", height=8)
    tree_ventas_mensual.heading("Mes", text="Mes (YYYY-MM)")
    tree_ventas_mensual.heading("Total Vendido", text="Total Vendido (Gs)")
    tree_ventas_mensual.column("Mes", width=150, anchor="center")
    tree_ventas_mensual.column("Total Vendido", width=200, anchor="e")
    tree_ventas_mensual.pack(pady=5, fill=tk.X, padx=10)

    ventas_por_mes_raw = obtener_ventas_por_mes()
    if not ventas_por_mes_raw:
        tree_ventas_mensual.insert("", tk.END, values=("No hay datos de ventas mensuales para mostrar.", ""))
    else:
        for mes_año, total in ventas_por_mes_raw.items():
            tree_ventas_mensual.insert("", tk.END, values=(mes_año, _formatear_moneda(total)))

    tk.Label(content_frame, text="Ventas Agrupadas por Semana", font=("Helvetica", 12, "bold")).pack(pady=(15, 5))
    tree_ventas_semanal = ttk.Treeview(content_frame, columns=("Semana", "Total Vendido"), show="headings", height=8)
    tree_ventas_semanal.heading("Semana", text="Semana (YYYY-WNN)")
    tree_ventas_semanal.heading("Total Vendido", text="Total Vendido (Gs)")
    tree_ventas_semanal.column("Semana", width=150, anchor="center")
    tree_ventas_semanal.column("Total Vendido", width=200, anchor="e")
    tree_ventas_semanal.pack(pady=5, fill=tk.X, padx=10)

    ventas_por_semana = obtener_ventas_por_semana()
    if not ventas_por_semana:
        tree_ventas_semanal.insert("", tk.END, values=("No hay datos de ventas semanales para mostrar.", ""))
    else:
        for semana_año, total in ventas_por_semana.items():
            tree_ventas_semanal.insert("", tk.END, values=(semana_año, _formatear_moneda(total)))

    tk.Label(content_frame, text="Ventas por Producto", font=("Helvetica", 12, "bold")).pack(pady=(15, 5))
    tree_ventas_producto = ttk.Treeview(content_frame, columns=("Producto", "Total Vendido"), show="headings", height=8)
    tree_ventas_producto.heading("Producto", text="Producto")
    tree_ventas_producto.heading("Total Vendido", text="Total Vendido (Gs)")
    tree_ventas_producto.column("Producto", width=150, anchor="center")
    tree_ventas_producto.column("Total Vendido", width=200, anchor="e")
    tree_ventas_producto.pack(pady=5, fill=tk.X, padx=10)

    ventas_por_producto = obtener_ventas_por_producto()
    if not ventas_por_producto:
        tree_ventas_producto.insert("", tk.END, values=("No hay ventas por producto para mostrar.", ""))
    else:
        ventas_ordenadas = sorted(ventas_por_producto.items(), key=lambda x: x[1], reverse=True)
        for producto_id, total in ventas_ordenadas:
            prod = obtener_producto_por_id(producto_id)
            nombre = prod.nombre if prod else str(producto_id)
            total_str = f"Gs {total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tree_ventas_producto.insert("", tk.END, values=(nombre, total_str))

    tk.Label(content_frame, text="Compras Agrupadas por Mes", font=("Helvetica", 12, "bold")).pack(pady=(15, 5))
    tree_compras_mensual = ttk.Treeview(content_frame, columns=("Mes", "Total Comprado"), show="headings", height=8)
    tree_compras_mensual.heading("Mes", text="Mes (YYYY-MM)")
    tree_compras_mensual.heading("Total Comprado", text="Total Comprado (Gs)")
    tree_compras_mensual.column("Mes", width=150, anchor="center")
    tree_compras_mensual.column("Total Comprado", width=200, anchor="e")
    tree_compras_mensual.pack(pady=5, fill=tk.X, padx=10)

    compras_por_mes_raw = obtener_compras_por_mes()
    if not compras_por_mes_raw:
        tree_compras_mensual.insert("", tk.END, values=("No hay datos de compras mensuales para mostrar.", ""))
    else:
        for mes_año, total in compras_por_mes_raw:
            tree_compras_mensual.insert("", tk.END, values=(mes_año, total))

    tk.Label(content_frame, text="Compras Agrupadas por Semana", font=("Helvetica", 12, "bold")).pack(pady=(15, 5))
    tree_compras_semanal = ttk.Treeview(content_frame, columns=("Semana", "Total Comprado"), show="headings", height=8)
    tree_compras_semanal.heading("Semana", text="Semana (YYYY-WNN)")
    tree_compras_semanal.heading("Total Comprado", text="Total Comprado (Gs)")
    tree_compras_semanal.column("Semana", width=150, anchor="center")
    tree_compras_semanal.column("Total Comprado", width=200, anchor="e")
    tree_compras_semanal.pack(pady=5, fill=tk.X, padx=10)

    compras_por_semana = obtener_compras_por_semana()
    if not compras_por_semana:
        tree_compras_semanal.insert("", tk.END, values=("No hay datos de compras semanales para mostrar.", ""))
    else:
        for semana_año, total in compras_por_semana:
            tree_compras_semanal.insert("", tk.END, values=(semana_año, total))

    total_ventas_general = total_vendido_tickets()
    total_compras_general = total_comprado()
    balance_general = total_ventas_general - total_compras_general
    balance_formateado = _formatear_moneda(balance_general)
    color_balance = "green" if balance_general >= 0 else "red"

    tk.Label(content_frame, text="--- Balance General ---", font=("Helvetica", 14, "bold")).pack(pady=(20, 5))
    tk.Label(
        content_frame,
        text=f"Total Ventas: {_formatear_moneda(total_ventas_general)}",
        font=("Helvetica", 12),
    ).pack()
    tk.Label(
        content_frame,
        text=f"Total Compras: {_formatear_moneda(total_compras_general)}",
        font=("Helvetica", 12),
    ).pack()
    tk.Label(
        content_frame,
        text=f"Balance Neto: {balance_formateado}",
        font=("Helvetica", 14, "bold"),
        fg=color_balance,
    ).pack(pady=5)

    tk.Label(content_frame, text="Gráfico de Ventas y Compras Mensuales", font=("Helvetica", 12, "bold")).pack(pady=(20, 5))

    meses_ventas = [item[0] for item in ventas_por_mes_raw]
    valores_ventas = [float(item[1].replace("Gs ", "").replace(".", "").replace(",", ".")) for item in ventas_por_mes_raw]
    meses_compras = [item[0] for item in compras_por_mes_raw]
    valores_compras = [float(item[1].replace("Gs ", "").replace(".", "").replace(",", ".")) for item in compras_por_mes_raw]

    all_meses = sorted(list(set(meses_ventas + meses_compras)))
    ventas_dict = dict(zip(meses_ventas, valores_ventas))
    compras_dict = dict(zip(meses_compras, valores_compras))
    ventas_para_chart = [ventas_dict.get(mes, 0) for mes in all_meses]
    compras_para_chart = [compras_dict.get(mes, 0) for mes in all_meses]

    if not all_meses:
        tk.Label(
            content_frame,
            text="No hay datos suficientes para generar el gráfico mensual.",
            font=("Helvetica", 10, "italic"),
        ).pack(pady=10)
    else:
        fig, ax = plt.subplots(figsize=(7, 4))
        bar_width = 0.35
        index = np.arange(len(all_meses))
        ax.bar(index - bar_width / 2, ventas_para_chart, bar_width, label="Ventas (Gs)", color="skyblue")
        ax.bar(index + bar_width / 2, compras_para_chart, bar_width, label="Compras (Gs)", color="lightcoral")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Monto (Gs)")
        ax.set_title("Ventas y Compras Mensuales")
        ax.set_xticks(index)
        ax.set_xticklabels(all_meses, rotation=45, ha="right")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        canvas_chart = FigureCanvasTkAgg(fig, master=content_frame)
        canvas_widget = canvas_chart.get_tk_widget()
        toolbar = NavigationToolbar2Tk(canvas_chart, content_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X, expand=False)
        canvas_widget.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        canvas_chart.draw()
        plt.close(fig)

    content_frame.update_idletasks()
    main_canvas.config(scrollregion=main_canvas.bbox("all"))
