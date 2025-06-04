import tkinter as tk
from tkinter import ttk # Importar ttk para widgets estilizados
from gui.productos_view import mostrar_ventana_productos
from gui.ventas_view import mostrar_ventana_ventas
from gui.informes_view import mostrar_ventana_informes
from gui.estadisticas_view import mostrar_ventana_estadisticas
from gui.compras_view import mostrar_ventana_compras
from gui.compras_historial_view import mostrar_ventana_historial_compras
from gui.materia_prima_view import mostrar_ventana_materias_primas
from gui.recetas_view import mostrar_ventana_recetas # ¡Nueva importación!

def iniciar_app():
    root = tk.Tk()
    root.title("Sistema de Ventas - Cafetería")
    root.geometry("500x800") # Aumenta el tamaño para acomodar el nuevo botón y espaciado
    root.resizable(False, False) # Hace la ventana no redimensionable
    root.configure(bg="#F0F0F0") # Un gris claro para un fondo minimalista

    # Estilo general para los botones (usando ttk)
    style = ttk.Style()
    style.configure("TButton",
                    font=("Segoe UI", 11, "bold"), # Fuente moderna y limpia
                    foreground="#333333", # Texto gris oscuro
                    background="#E0E0E0", # Fondo gris claro para los botones
                    padding=[15, 10], # Mayor padding para un look más espacioso
                    relief="flat", # Sin relieve para un aspecto plano
                    borderwidth=0, # Sin borde
                    focuscolor="#D0D0D0") # Color al enfocar
    style.map("TButton",
              background=[("active", "#D0D0D0")], # Un gris ligeramente más oscuro al pasar el mouse
              foreground=[("active", "#000000")]) # Texto más oscuro al pasar el mouse

    # Estilo específico para el botón de Salir
    style.configure("Exit.TButton",
                    background="#FF6B6B", # Rojo suave para salir
                    foreground="white")
    style.map("Exit.TButton",
              background=[("active", "#FF8C8C")]) # Rojo más claro al pasar el mouse

    # Etiqueta del título principal
    tk.Label(root,
             text="Sistema de Gestión de Cafetería",
             font=("Segoe UI", 18, "bold"), # Fuente ligeramente más pequeña
             bg="#F0F0F0", # Mismo color de fondo que la ventana
             fg="#222222").pack(pady=(40, 30)) # Más padding superior para centrar

    # Frame para los botones principales para mejor organización
    button_frame = tk.Frame(root, bg="#F0F0F0") # Mismo color de fondo
    button_frame.pack(pady=10, fill=tk.X, padx=50) # Añade padding horizontal para centrar los botones

    # Botones principales (ahora usando ttk.Button)
    ttk.Button(button_frame, text="Gestionar Productos", command=mostrar_ventana_productos).pack(pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Gestionar Materias Primas", command=mostrar_ventana_materias_primas).pack(pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Gestionar Recetas", command=mostrar_ventana_recetas).pack(pady=10, fill=tk.X) # ¡Nuevo botón!
    ttk.Button(button_frame, text="Registrar Venta", command=mostrar_ventana_ventas).pack(pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Registrar Compra", command=mostrar_ventana_compras).pack(pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Ver Historial de Ventas", command=mostrar_ventana_informes).pack(pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Ver Historial de Compras", command=mostrar_ventana_historial_compras).pack(pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Ver Estadísticas", command=mostrar_ventana_estadisticas).pack(pady=10, fill=tk.X)

    # Botón de Salir (con un color diferente)
    ttk.Button(root, text="Salir", command=root.destroy, style="Exit.TButton").pack(pady=(30, 20), fill=tk.X, padx=50) # Más padding y centrado

    root.mainloop()
