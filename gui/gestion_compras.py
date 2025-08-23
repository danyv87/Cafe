import tkinter as tk
from tkinter import messagebox
from controllers.compras_controller import listar_compras, eliminar_compra


def mostrar_ventana_gestion_compras():
    ventana = tk.Toplevel()
    ventana.title("Eliminar compras")
    ventana.geometry("700x400")

    tk.Label(ventana, text="Historial de Compras", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))

    lista = tk.Listbox(ventana, width=90, height=14)
    lista.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def actualizar_lista():
        lista.delete(0, tk.END)
        global compras
        compras = listar_compras()
        if not compras:
            lista.insert(tk.END, "No hay compras registradas.")
            return
        for c in compras:
            id_corto = c.id[:8] if len(str(c.id)) > 8 else c.id
            total = f"{c.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, f"ID: {id_corto} | Proveedor: {c.proveedor_id} | Total: Gs {total}")

    def eliminar_seleccion():
        seleccion = lista.curselection()
        if not seleccion or not compras or "No hay compras" in lista.get(0):
            messagebox.showwarning("Advertencia", "Selecciona una compra para eliminar.")
            return
        index = seleccion[0]
        compra_id = compras[index].id
        confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la compra ID {compra_id}?")
        if confirm:
            try:
                eliminar_compra(compra_id)
                messagebox.showinfo("Éxito", "Compra eliminada correctamente.")
                actualizar_lista()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

    btn_eliminar = tk.Button(ventana, text="Eliminar compra seleccionada", command=eliminar_seleccion, bg="red", fg="white")
    btn_eliminar.pack(pady=5)

    actualizar_lista()
    return ventana

