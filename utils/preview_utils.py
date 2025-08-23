import tkinter as tk
from PIL import Image, ImageTk


def mostrar_imagen(path: str):
    """Abrir una imagen y mostrarla en una ventana Toplevel."""
    ventana = tk.Toplevel()
    ventana.title("Vista previa de factura")
    imagen = Image.open(path)
    photo = ImageTk.PhotoImage(imagen)
    label = tk.Label(ventana, image=photo)
    label.image = photo  # Mantener referencia
    label.pack()

