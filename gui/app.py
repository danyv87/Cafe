import tkinter as tk
from gui.productos_view import mostrar_ventana_productos
from gui.ventas_view import mostrar_ventana_ventas
from gui.informes_view import mostrar_ventana_informes
from gui.estadisticas_view import mostrar_ventana_estadisticas # ¡Nueva importación!

def iniciar_app():
    root = tk.Tk()
    root.title("Sistema de Ventas - Cafetería")
    root.geometry("400x350") # Aumenta ligeramente el tamaño para el nuevo botón

    tk.Label(root, text="Sistema de Ventas - Cafetería", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Gestionar Productos", width=30, command=mostrar_ventana_productos).pack(pady=10)
    tk.Button(root, text="Registrar Venta", width=30, command=mostrar_ventana_ventas).pack(pady=10)
    tk.Button(root, text="Ver Historial de Ventas", width=30, command=mostrar_ventana_informes).pack(pady=10)
    tk.Button(root, text="Ver Estadísticas", width=30, command=mostrar_ventana_estadisticas).pack(pady=10) # ¡Nuevo botón!

    tk.Button(root, text="Salir", width=30, command=root.destroy).pack(pady=20)

    root.mainloop()
