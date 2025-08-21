"""Módulo para mostrar la ventana de Informes y Análisis.

Combina un enfoque orientado a objetos para las pestañas de historial de
ventas y compras mediante la clase ``HistoryReportFrame`` y funciones
modulares para las otras pestañas disponibles.
"""

import tkinter as tk
from tkinter import ttk

from controllers.tickets_controller import listar_tickets, total_vendido_tickets
from controllers.compras_controller import listar_compras, total_comprado
from controllers.proveedores_controller import obtener_proveedor_por_id

from gui.estadisticas_view import agregar_tab_estadisticas
from gui.rentabilidad_view import agregar_tab_rentabilidad
from gui.costos_operativos_view import agregar_tab_costos_operativos
from gui.reportes_financieros_view import agregar_tab_estado_resultado


class HistoryReportFrame:
    """Crear las pestañas de historial de ventas y compras."""

    def __init__(self, notebook: ttk.Notebook) -> None:
        self.notebook = notebook
        self._agregar_tab_historial_ventas()
        self._agregar_tab_historial_compras()

    def _agregar_tab_historial_ventas(self) -> None:
        """Agregar una pestaña con el historial de tickets de ventas."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Historial de Ventas")

        frame_lista = ttk.Frame(frame)
        frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL)
        lista = tk.Listbox(frame_lista, width=80, yscrollcommand=scrollbar.set)
        scrollbar.config(command=lista.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tickets = listar_tickets()
        if not tickets:
            lista.insert(tk.END, "No hay tickets registrados.")
        else:
            for t in tickets:
                total_ticket_formateado = (
                    f"{t.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                lista.insert(tk.END, "----------------------------------------------------------------------")
                lista.insert(
                    tk.END,
                    f"Ticket ID: {t.id[:8]}... | Fecha: {t.fecha} | Cliente: {t.cliente} | Total Ticket: Gs {total_ticket_formateado}",
                )
                lista.insert(tk.END, "  Productos:")
                for item in t.items_venta:
                    total_item_formateado = (
                        f"{item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                    lista.insert(
                        tk.END,
                        f"    - {item.cantidad} x {item.nombre_producto} @ Gs {item.precio_unitario:.0f} = Gs {total_item_formateado}",
                    )
                lista.insert(tk.END, "----------------------------------------------------------------------")

        total_general = total_vendido_tickets()
        total_general_formateado = (
            f"{total_general:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        ttk.Label(
            frame,
            text=f"Total General Vendido: Gs {total_general_formateado}",
            font=("Helvetica", 14, "bold"),
            foreground="darkgreen",
        ).pack(pady=10)

    def _agregar_tab_historial_compras(self) -> None:
        """Agregar una pestaña con el historial de compras."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Historial de Compras")

        ttk.Label(frame, text="Historial de Compras", font=("Helvetica", 16, "bold")).pack(pady=10)

        frame_lista = ttk.Frame(frame)
        frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL)
        lista = tk.Listbox(frame_lista, width=90, yscrollcommand=scrollbar.set)
        scrollbar.config(command=lista.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        compras = listar_compras()
        if not compras:
            lista.insert(tk.END, "No hay compras registradas.")
        else:
            for c in compras:
                total_compra_formateado = (
                    f"{c.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                lista.insert(tk.END, "---------------------------------------------------------------------------------")
                proveedor = obtener_proveedor_por_id(c.proveedor_id)
                nombre_proveedor = proveedor.nombre if proveedor else c.proveedor_id
                lista.insert(
                    tk.END,
                    f"Compra ID: {c.id[:8]}... | Fecha: {c.fecha} | Proveedor: {nombre_proveedor} | Total Compra: Gs {total_compra_formateado}",
                )
                lista.insert(tk.END, "  Items Comprados:")
                for item in c.items_compra:
                    total_item_formateado = (
                        f"{item.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                    item_display_text = f"    - {item.cantidad} x {item.nombre_producto}"
                    if item.descripcion_adicional:
                        item_display_text += f" ({item.descripcion_adicional})"
                    item_display_text += (
                        f" @ Gs {item.costo_unitario:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        + f" = Gs {total_item_formateado}"
                    )
                    lista.insert(tk.END, item_display_text)
                lista.insert(tk.END, "---------------------------------------------------------------------------------")

        total_general_compras = total_comprado()
        total_general_compras_formateado = (
            f"{total_general_compras:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        ttk.Label(
            frame,
            text=f"Total General Comprado: Gs {total_general_compras_formateado}",
            font=("Helvetica", 14, "bold"),
            foreground="darkred",
        ).pack(pady=10)


def mostrar_informes_menu() -> None:
    """Abrir la ventana de informes con todas las pestañas disponibles."""
    ventana = tk.Toplevel()
    ventana.title("Informes y Análisis")
    ventana.geometry("900x700")

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True)

    HistoryReportFrame(notebook)
    agregar_tab_estadisticas(notebook)
    agregar_tab_rentabilidad(notebook)
    agregar_tab_costos_operativos(notebook)
    agregar_tab_estado_resultado(notebook)

