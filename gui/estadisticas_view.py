import tkinter as tk
from tkinter import ttk  # Importar ttk para Treeview
from controllers.tickets_controller import obtener_ventas_por_mes, obtener_ventas_por_semana, total_vendido_tickets
from controllers.compras_controller import obtener_compras_por_mes, obtener_compras_por_semana, total_comprado

# Importaciones para el gráfico
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # ¡Importación corregida!
import numpy as np  # Necesario para el arreglo de posiciones de las barras


def mostrar_ventana_estadisticas():
    ventana = tk.Toplevel()
    ventana.title("Estadísticas de Ventas y Compras")
    ventana.geometry("800x950")  # Aumenta el tamaño para acomodar el gráfico y más contenido
    ventana.resizable(True, True)  # Permitir redimensionar la ventana

    # Crear un Canvas principal para permitir el scroll
    main_canvas = tk.Canvas(ventana)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Crear un scrollbar para el Canvas principal
    scrollbar_main = ttk.Scrollbar(ventana, orient=tk.VERTICAL, command=main_canvas.yview)
    scrollbar_main.pack(side=tk.RIGHT, fill=tk.Y)

    # Configurar el Canvas para usar el scrollbar
    main_canvas.configure(yscrollcommand=scrollbar_main.set)
    main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

    # Crear un Frame dentro del Canvas para contener todos los widgets
    content_frame = tk.Frame(main_canvas)
    main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    tk.Label(content_frame, text="Estadísticas de Ventas y Compras", font=("Helvetica", 18, "bold")).pack(pady=10)

    # --- Sección de Estadísticas Mensuales de Ventas ---
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
        for mes_año, total in ventas_por_mes_raw:
            tree_ventas_mensual.insert("", tk.END, values=(mes_año, total))

    # --- Sección de Estadísticas Semanales de Ventas ---
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
        for semana_año, total in ventas_por_semana:
            tree_ventas_semanal.insert("", tk.END, values=(semana_año, total))

    # --- Sección de Estadísticas Mensuales de Compras ---
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

    # --- Sección de Estadísticas Semanales de Compras ---
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

    # --- Sección de Balance General ---
    total_ventas_general = total_vendido_tickets()
    total_compras_general = total_comprado()
    balance_general = total_ventas_general - total_compras_general

    # Formatear el balance con separador de miles y signo de moneda
    balance_formateado = f"{balance_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    color_balance = "green" if balance_general >= 0 else "red"

    tk.Label(content_frame, text="--- Balance General ---", font=("Helvetica", 14, "bold")).pack(pady=(20, 5))
    tk.Label(content_frame,
             text=f"Total Ventas: Gs {total_ventas_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
             font=("Helvetica", 12)).pack()
    tk.Label(content_frame,
             text=f"Total Compras: Gs {total_compras_general:,.0f}".replace(",", "X").replace(".", ",").replace("X",
                                                                                                                "."),
             font=("Helvetica", 12)).pack()
    tk.Label(content_frame, text=f"Balance Neto: Gs {balance_formateado}", font=("Helvetica", 14, "bold"),
             fg=color_balance).pack(pady=5)

    # --- Sección del Gráfico ---
    tk.Label(content_frame, text="Gráfico de Ventas y Compras Mensuales", font=("Helvetica", 12, "bold")).pack(
        pady=(20, 5))

    # Preparar datos para el gráfico
    meses_ventas = [item[0] for item in ventas_por_mes_raw]
    # Eliminar "Gs " y reemplazar separadores para convertir a float
    valores_ventas = [float(item[1].replace("Gs ", "").replace(".", "").replace(",", ".")) for item in
                      ventas_por_mes_raw]

    meses_compras = [item[0] for item in compras_por_mes_raw]
    valores_compras = [float(item[1].replace("Gs ", "").replace(".", "").replace(",", ".")) for item in
                       compras_por_mes_raw]

    # Combinar meses únicos y ordenarlos
    all_meses = sorted(list(set(meses_ventas + meses_compras)))

    # Crear diccionarios para fácil acceso a los totales por mes
    ventas_dict = dict(zip(meses_ventas, valores_ventas))
    compras_dict = dict(zip(meses_compras, valores_compras))

    # Asegurarse de que todos los meses tengan un valor (0 si no hay ventas/compras)
    ventas_para_chart = [ventas_dict.get(mes, 0) for mes in all_meses]
    compras_para_chart = [compras_dict.get(mes, 0) for mes in all_meses]

    if not all_meses:  # Si no hay datos para el gráfico
        tk.Label(content_frame, text="No hay datos suficientes para generar el gráfico mensual.",
                 font=("Helvetica", 10, "italic")).pack(pady=10)
    else:
        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(7, 4))  # Ajusta el tamaño de la figura

        bar_width = 0.35
        index = np.arange(len(all_meses))

        bar1 = ax.bar(index - bar_width / 2, ventas_para_chart, bar_width, label='Ventas (Gs)', color='skyblue')
        bar2 = ax.bar(index + bar_width / 2, compras_para_chart, bar_width, label='Compras (Gs)', color='lightcoral')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Monto (Gs)')
        ax.set_title('Ventas y Compras Mensuales')
        ax.set_xticks(index)
        ax.set_xticklabels(all_meses, rotation=45, ha="right")  # Rotar etiquetas para mejor legibilidad
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()  # Ajusta el layout para evitar superposiciones

        # Integrar el gráfico en Tkinter
        canvas_chart = FigureCanvasTkAgg(fig, master=content_frame)
        canvas_widget = canvas_chart.get_tk_widget()

        # Opcional: Barra de herramientas para el gráfico (zoom, pan, guardar)
        toolbar = NavigationToolbar2Tk(canvas_chart, content_frame)  # ¡Instanciación corregida!
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X, expand=False)  # Empaquetar la barra de herramientas primero

        canvas_widget.pack(pady=10, padx=10, fill=tk.BOTH,
                           expand=True)  # Empaquetar el widget del canvas para que ocupe el resto del espacio
        canvas_chart.draw()  # ¡Asegura que el gráfico se dibuje!
        plt.close(fig)  # Cierra la figura de matplotlib para liberar memoria

    # Asegurarse de que el scrollbar se actualice correctamente
    content_frame.update_idletasks()
    main_canvas.config(scrollregion=main_canvas.bbox("all"))
