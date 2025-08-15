import tkinter as tk
from tkinter import ttk
from gui.informes_view import agregar_tab_historial_ventas
from gui.compras_historial_view import agregar_tab_historial_compras
from gui.estadisticas_view import agregar_tab_estadisticas
from gui.rentabilidad_view import agregar_tab_rentabilidad
from gui.costos_operativos_view import agregar_tab_costos_operativos


def mostrar_reportes_menu() -> None:
    """Abrir la ventana de informes con todas las pestañas disponibles."""
    ventana = tk.Toplevel()
    ventana.title("Informes y Análisis")
    ventana.geometry("900x700")

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True)

    agregar_tab_historial_ventas(notebook)
    agregar_tab_historial_compras(notebook)
    agregar_tab_estadisticas(notebook)
    agregar_tab_rentabilidad(notebook)
    agregar_tab_costos_operativos(notebook)
