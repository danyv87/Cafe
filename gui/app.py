import tkinter as tk
from gui.productos_view import mostrar_ventana_productos
from gui.ventas_view import mostrar_ventana_ventas # Ahora ventas_view gestionará tickets
from gui.informes_view import mostrar_ventana_informes # Ahora informes_view mostrará tickets

def iniciar_app():
    root = tk.Tk()
    root.title("Sistema de Ventas - Cafetería")
    root.geometry("400x300")

    tk.Label(root, text="Sistema de Ventas - Cafetería", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Gestionar Productos", width=30, command=mostrar_ventana_productos).pack(pady=10)
    tk.Button(root, text="Registrar Venta", width=30, command=mostrar_ventana_ventas).pack(pady=10)
    tk.Button(root, text="Ver Informes", width=30, command=mostrar_ventana_informes).pack(pady=10)

    tk.Button(root, text="Salir", width=30, command=root.destroy).pack(pady=20)

    root.mainloop()
