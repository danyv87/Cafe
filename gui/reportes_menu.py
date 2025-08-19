import tkinter as tk
from tkinter import ttk

from controllers.tickets_controller import listar_tickets, total_vendido_tickets
from controllers.compras_controller import listar_compras, total_comprado
from gui.components.history_report import HistoryReportFrame
from utils.format_utils import format_currency


def mostrar_reportes_menu():
    ventana = tk.Toplevel()
    ventana.title("Reportes")
    ventana.geometry("650x500")

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Historial de ventas
    tickets = listar_tickets()

    def format_ticket(ticket):
        lines = ["----------------------------------------------------------------------"]
        lines.append(
            f"Ticket ID: {ticket.id[:8]}... | Fecha: {ticket.fecha} | Cliente: {ticket.cliente} | Total Ticket: {format_currency(ticket.total)}"
        )
        lines.append("  Productos:")
        for item in ticket.items_venta:
            lines.append(
                f"    - {item.cantidad} x {item.nombre_producto} @ {format_currency(item.precio_unitario)} = {format_currency(item.total)}"
            )
        lines.append("----------------------------------------------------------------------")
        return lines

    frame_ventas = HistoryReportFrame(
        notebook, "Historial de Ventas", tickets, format_ticket, width=80
    )
    notebook.add(frame_ventas, text="Ventas")
    tk.Label(
        frame_ventas,
        text=f"Total General Vendido: {format_currency(total_vendido_tickets())}",
        font=("Helvetica", 14, "bold"),
        fg="darkgreen",
    ).pack(pady=10)

    # Historial de compras
    compras = listar_compras()

    def format_compra(compra):
        lines = ["---------------------------------------------------------------------------------"]
        lines.append(
            f"Compra ID: {compra.id[:8]}... | Fecha: {compra.fecha} | Proveedor: {compra.proveedor} | Total Compra: {format_currency(compra.total)}"
        )
        lines.append("  Items Comprados:")
        for item in compra.items_compra:
            item_text = f"    - {item.cantidad} x {item.nombre_producto}"
            if getattr(item, "descripcion_adicional", ""):
                item_text += f" ({item.descripcion_adicional})"
            item_text += (
                f" @ {format_currency(item.costo_unitario)} = {format_currency(item.total)}"
            )
            lines.append(item_text)
        lines.append("---------------------------------------------------------------------------------")
        return lines

    frame_compras = HistoryReportFrame(
        notebook, "Historial de Compras", compras, format_compra
    )
    notebook.add(frame_compras, text="Compras")
    tk.Label(
        frame_compras,
        text=f"Total General Comprado: {format_currency(total_comprado())}",
        font=("Helvetica", 14, "bold"),
        fg="darkred",
    ).pack(pady=10)
