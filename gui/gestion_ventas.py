import tkinter as tk
from tkinter import messagebox
from controllers.tickets_controller import listar_tickets, eliminar_ticket

def mostrar_ventana_gestion_ventas():
    ventana = tk.Toplevel()
    ventana.title("Eliminar ventas")
    ventana.geometry("700x400")

    tk.Label(ventana, text="Historial de Ventas", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))

    lista = tk.Listbox(ventana, width=90, height=14)
    lista.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def actualizar_lista():
        lista.delete(0, tk.END)
        global tickets
        tickets = listar_tickets()
        if not tickets:
            lista.insert(tk.END, "No hay ventas registradas.")
            return
        for t in tickets:
            id_corto = t.id[:8] if len(str(t.id)) > 8 else t.id
            total = f"{t.total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lista.insert(tk.END, f"ID: {id_corto} | Cliente: {t.cliente} | Total: Gs {total}")

    def eliminar_seleccion():
        seleccion = lista.curselection()
        if not seleccion or not tickets or "No hay ventas" in lista.get(0):
            messagebox.showwarning("Advertencia", "Selecciona una venta para eliminar.")
            return
        index = seleccion[0]
        ticket_id = tickets[index].id
        confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el ticket ID {ticket_id}?")
        if confirm:
            try:
                eliminar_ticket(ticket_id)
                messagebox.showinfo("Éxito", "Venta eliminada correctamente.")
                actualizar_lista()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

    btn_eliminar = tk.Button(ventana, text="Eliminar venta seleccionada", command=eliminar_seleccion, bg="red", fg="white")
    btn_eliminar.pack(pady=5)

    actualizar_lista()