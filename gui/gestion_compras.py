"""Ventana para eliminar compras registradas.

Permite seleccionar una compra y eliminarla. La operación revierte
el stock que se había sumado al registrar la compra.
"""

import tkinter as tk
from tkinter import messagebox

from controllers.compras_controller import listar_compras, eliminar_compra
from controllers.proveedores_controller import obtener_proveedor_por_id


def mostrar_ventana_gestion_compras():
    """Mostrar una ventana para eliminar compras y revertir su stock.

    La lista muestra cada compra registrada junto con su proveedor y total.
    Al eliminar una compra se resta del stock la cantidad correspondiente a
    cada materia prima involucrada. Si el stock actual no permite la
    reversión, se lanzará un ``ValueError`` desde el controlador.
    """
    ventana = tk.Toplevel()
    ventana.title("Eliminar compras")
    ventana.geometry("700x400")

    tk.Label(ventana, text="Historial de Compras", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))

    lista = tk.Listbox(ventana, width=90, height=14)
    lista.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def actualizar_lista():
        """Recargar la lista de compras desde el almacenamiento."""
        lista.delete(0, tk.END)
        global compras
        compras = listar_compras()
        if not compras:
            lista.insert(tk.END, "No hay compras registradas.")
            return
        for c in compras:
            id_corto = c.id[:8] if len(str(c.id)) > 8 else c.id
            proveedor = obtener_proveedor_por_id(c.proveedor_id)
            nombre_prov = proveedor.nombre if proveedor else c.proveedor_id
            total = f"{c.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, f"ID: {id_corto} | Proveedor: {nombre_prov} | Total: Gs {total}")

    def eliminar_seleccion():
        """Eliminar la compra seleccionada tras confirmar con el usuario."""
        seleccion = lista.curselection()
        if not seleccion or not compras or "No hay compras" in lista.get(0):
            messagebox.showwarning("Advertencia", "Selecciona una compra para eliminar.")
            return
        index = seleccion[0]
        compra = compras[index]
        confirm = messagebox.askyesno(
            "Confirmar",
            "¿Eliminar la compra seleccionada? Esta acción revertirá el stock registrado.",
        )
        if confirm:
            try:
                eliminar_compra(compra.id)
                messagebox.showinfo("Éxito", "Compra eliminada correctamente.")
                actualizar_lista()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

    tk.Button(ventana, text="Eliminar compra seleccionada", command=eliminar_seleccion, bg="red", fg="white").pack(pady=5)

    actualizar_lista()
