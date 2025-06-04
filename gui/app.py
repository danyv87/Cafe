import tkinter as tk
from tkinter import ttk # Importar ttk para widgets estilizados
from gui.productos_view import mostrar_ventana_productos
from gui.ventas_view import mostrar_ventana_ventas
from gui.informes_view import mostrar_ventana_informes
from gui.estadisticas_view import mostrar_ventana_estadisticas
from gui.compras_view import mostrar_ventana_compras
from gui.compras_historial_view import mostrar_ventana_historial_compras
from gui.materia_prima_view import mostrar_ventana_materias_primas
from gui.recetas_view import mostrar_ventana_recetas
from gui.rentabilidad_view import mostrar_ventana_rentabilidad

def iniciar_app():
    root = tk.Tk()
    root.title("Sistema de Ventas - Cafetería")
    root.geometry("600x850") # Tamaño aumentado para una mejor distribución
    root.resizable(False, False) # Hace la ventana no redimensionable
    root.configure(bg="#F0F0F0") # Un gris claro para un fondo minimalista

    # --- Configuración de Estilos (ttk.Style) ---
    style = ttk.Style()
    style.theme_use("clam") # Un tema más moderno para ttk

    # Estilo general para los LabelFrames
    style.configure("TFrame", background="#F0F0F0")
    style.configure("TLabelframe",
                    background="#F0F0F0",
                    font=("Segoe UI", 12, "bold"),
                    foreground="#444444")
    style.configure("TLabelframe.Label", background="#F0F0F0", foreground="#444444")

    # Estilo general para los botones
    style.configure("TButton",
                    font=("Segoe UI", 11, "bold"),
                    foreground="#333333",
                    background="#E0E0E0",
                    padding=[15, 10],
                    relief="flat",
                    borderwidth=0,
                    focuscolor="#D0D0D0")
    style.map("TButton",
              background=[("active", "#D0D0D0")],
              foreground=[("active", "#000000")])

    # Estilo específico para el botón de Salir
    style.configure("Exit.TButton",
                    background="#FF6B6B",
                    foreground="white")
    style.map("Exit.TButton",
              background=[("active", "#FF8C8C")])

    # --- Widgets de la Interfaz ---

    # Etiqueta del título principal
    tk.Label(root,
             text="Sistema de Gestión de Cafetería",
             font=("Segoe UI", 20, "bold"),
             bg="#F0F0F0",
             fg="#222222").pack(pady=(30, 20))

    # Frame principal para todos los grupos de botones
    main_button_container = ttk.Frame(root, padding=20)
    main_button_container.pack(pady=10, fill=tk.BOTH, expand=True, padx=30)

    # --- Grupo: Gestión de Datos Maestros ---
    frame_master_data = ttk.LabelFrame(main_button_container, text="Gestión de Datos Maestros", padding=15)
    frame_master_data.pack(pady=10, fill=tk.X)
    ttk.Button(frame_master_data, text="Gestionar Productos", command=mostrar_ventana_productos).pack(pady=5, fill=tk.X)
    ttk.Button(frame_master_data, text="Gestionar Materias Primas", command=mostrar_ventana_materias_primas).pack(pady=5, fill=tk.X)
    ttk.Button(frame_master_data, text="Gestionar Recetas", command=mostrar_ventana_recetas).pack(pady=5, fill=tk.X)

    # --- Grupo: Operaciones Diarias ---
    frame_daily_ops = ttk.LabelFrame(main_button_container, text="Operaciones Diarias", padding=15)
    frame_daily_ops.pack(pady=10, fill=tk.X)
    ttk.Button(frame_daily_ops, text="Registrar Venta", command=mostrar_ventana_ventas).pack(pady=5, fill=tk.X)
    ttk.Button(frame_daily_ops, text="Registrar Compra", command=mostrar_ventana_compras).pack(pady=5, fill=tk.X)

    # --- Grupo: Informes y Análisis ---
    frame_reports = ttk.LabelFrame(main_button_container, text="Informes y Análisis", padding=15)
    frame_reports.pack(pady=10, fill=tk.X)
    ttk.Button(frame_reports, text="Ver Historial de Ventas", command=mostrar_ventana_informes).pack(pady=5, fill=tk.X)
    ttk.Button(frame_reports, text="Ver Historial de Compras", command=mostrar_ventana_historial_compras).pack(pady=5, fill=tk.X)
    ttk.Button(frame_reports, text="Ver Estadísticas", command=mostrar_ventana_estadisticas).pack(pady=5, fill=tk.X)
    ttk.Button(frame_reports, text="Ver Rentabilidad", command=mostrar_ventana_rentabilidad).pack(pady=5, fill=tk.X)

    # Botón de Salir
    ttk.Button(root, text="Salir", command=root.destroy, style="Exit.TButton").pack(pady=(30, 20), fill=tk.X, padx=50)

    root.mainloop()
