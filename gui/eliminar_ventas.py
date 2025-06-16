import tkinter as tk
from tkinter import messagebox
from controllers.tickets_controller import listar_tickets, eliminar_ticket

def actualizar_lista():
    lista.delete(0, tk.END)
    global tickets
    tickets = listar_tickets()
    for t in tickets:
        # Puedes mostrar más campos relevantes aquí
        lista.insert(tk.END, f"ID: {t.id} | Cliente: {t.cliente} | Total: {t.total}")

def eliminar_seleccion():
    seleccion = lista.curselection()
    if not seleccion:
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

root = tk.Tk()
root.title("Eliminar ventas")

lista = tk.Listbox(root, width=60)
lista.pack(padx=10, pady=10)

btn_eliminar = tk.Button(root, text="Eliminar venta seleccionada", command=eliminar_seleccion)
btn_eliminar.pack(pady=5)

actualizar_lista()
root.mainloop()