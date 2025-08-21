import tkinter as tk
from tkinter import ttk
from controllers.reportes_financieros import estado_resultado


def agregar_tab_estado_resultado(notebook: ttk.Notebook) -> None:
    """Agregar una pestaña que muestra el estado de resultados."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Estado Resultado")

    ttk.Label(frame, text="Estado de Resultados", font=("Helvetica", 16, "bold")).pack(pady=15)

    form = ttk.Frame(frame)
    form.pack(pady=10)

    ttk.Label(form, text="Inicio (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
    entry_inicio = ttk.Entry(form)
    entry_inicio.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form, text="Fin (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    entry_fin = ttk.Entry(form)
    entry_fin.grid(row=1, column=1, padx=5, pady=5)

    resultado_lbl = ttk.Label(frame, text="")
    resultado_lbl.pack(pady=10)

    def formato(valor: float) -> str:
        return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def generar():
        inicio = entry_inicio.get().strip()
        fin = entry_fin.get().strip()
        if not inicio or not fin:
            resultado_lbl.config(text="Debe ingresar fechas válidas.")
            return
        try:
            reporte = estado_resultado(inicio, fin)
        except Exception as e:
            resultado_lbl.config(text=str(e))
            return
        texto = (
            f"Ventas: Gs {formato(reporte['ventas'])}\n"
            f"Costos de producción: Gs {formato(reporte['costos_produccion'])}\n"
            f"Gastos adicionales: Gs {formato(reporte['gastos_adicionales'])}\n"
            f"Resultado neto: Gs {formato(reporte['resultado_neto'])}"
        )
        resultado_lbl.config(text=texto)

    ttk.Button(form, text="Generar", command=generar).grid(row=2, column=0, columnspan=2, pady=10)
