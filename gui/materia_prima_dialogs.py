"""Funciones de interacción para solicitar datos de materias primas faltantes.

Este módulo forma parte de la capa de presentación y contiene la lógica de
interacción con el usuario (GUI/CLI) para recopilar información sobre materias
primas que no están registradas.
"""

from typing import Dict, Tuple, List


def solicitar_datos_materia_prima(nombre: str):
    """Pide al usuario datos para crear una nueva materia prima o la omite.

    Retorna ``None`` si el usuario decide omitir la materia prima. Intenta usar
    diálogos de ``tkinter`` y cae a la entrada estándar si el entorno gráfico no
    está disponible.
    """

    try:  # pragma: no cover - prefer GUI but fall back to CLI in tests
        import tkinter as tk
        from tkinter import simpledialog

        root = tk.Tk()
        root.withdraw()
        accion = simpledialog.askstring(
            "Materia prima faltante",
            f"¿Desea crear u omitir '{nombre}'?",
            parent=root,
        )
        if accion is None or accion.strip().lower() != "crear":
            root.destroy()
            return None
        unidad = simpledialog.askstring(
            "Materia prima faltante",
            f"Unidad de medida para '{nombre}':",
            parent=root,
        )
        if unidad is None:
            raise ValueError("Operación cancelada por el usuario.")
        costo = simpledialog.askfloat(
            "Materia prima faltante",
            f"Costo unitario para '{nombre}':",
            parent=root,
        )
        if costo is None:
            raise ValueError("Operación cancelada por el usuario.")
        stock = simpledialog.askfloat(
            "Materia prima faltante",
            f"Stock inicial para '{nombre}':",
            parent=root,
        )
        if stock is None:
            raise ValueError("Operación cancelada por el usuario.")
        root.destroy()
        return unidad, float(costo), float(stock)
    except Exception:
        accion = (
            input(
                f"Materia prima '{nombre}' no encontrada. ¿Crear u omitir? (crear/omitir): "
            )
            .strip()
            .lower()
        )
        if accion != "crear":
            return None
        unidad = input(f"Ingrese la unidad de medida para '{nombre}': ").strip()
        costo = float(input(f"Ingrese el costo unitario para '{nombre}': "))
        stock = float(input(f"Ingrese el stock inicial para '{nombre}': "))
        return unidad, costo, stock


def solicitar_datos_materia_prima_masivo(
    faltantes: List[dict],
) -> Dict[str, Tuple[str, float, float]]:
    """Solicita datos de varias materias primas faltantes a la vez.

    Se intenta mostrar un formulario con ``tkinter`` para que el usuario pueda
    completar los datos de cada materia prima faltante y decidir cuáles crear.
    Si el entorno gráfico no está disponible, se recurre a la entrada estándar.

    Args:
        faltantes (list[dict]): Elementos detectados en el comprobante que no
            poseen una materia prima asociada.

    Returns:
        dict[str, tuple]: Diccionario ``{nombre: (unidad, costo, stock)}`` con
            los datos para las materias primas que el usuario decidió crear.
    """

    try:  # pragma: no cover - prefer GUI but fall back to CLI in tests
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.withdraw()

        top = tk.Toplevel(root)
        top.title("Materias primas faltantes")
        top.geometry("700x500")
        top.resizable(True, True)

        container = ttk.Frame(top, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        headers = ["Nombre", "Crear", "Unidad", "Costo", "Stock"]
        for col, text in enumerate(headers):
            ttk.Label(scrollable_frame, text=text, font=("Helvetica", 9, "bold")).grid(
                row=0, column=col, padx=5, pady=5
            )

        vars_crear: List[tk.BooleanVar] = []
        entradas_unidad: List[ttk.Entry] = []
        entradas_costo: List[ttk.Entry] = []
        entradas_stock: List[ttk.Entry] = []
        nombres: List[str] = []

        for idx, raw in enumerate(faltantes, start=1):
            nombre = raw.get("nombre_producto") or raw.get("producto") or ""
            nombres.append(nombre)

            ttk.Label(scrollable_frame, text=nombre).grid(row=idx, column=0, sticky="w")
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(scrollable_frame, variable=var)
            chk.grid(row=idx, column=1)

            e_unidad = ttk.Entry(scrollable_frame, width=10)
            e_unidad.grid(row=idx, column=2)
            e_costo = ttk.Entry(scrollable_frame, width=10)
            e_costo.grid(row=idx, column=3)
            e_stock = ttk.Entry(scrollable_frame, width=10)
            e_stock.grid(row=idx, column=4)

            vars_crear.append(var)
            entradas_unidad.append(e_unidad)
            entradas_costo.append(e_costo)
            entradas_stock.append(e_stock)

        resultado: Dict[str, Tuple[str, float, float]] = {}

        def aceptar():
            for i, nombre in enumerate(nombres):
                if vars_crear[i].get():
                    unidad = entradas_unidad[i].get().strip()
                    try:
                        costo = float(entradas_costo[i].get())
                        stock = float(entradas_stock[i].get())
                    except ValueError:
                        continue
                    resultado[nombre] = (unidad, costo, stock)
            top.destroy()
            root.quit()

        ttk.Button(top, text="Aceptar", command=aceptar).pack(pady=5)

        root.mainloop()
        root.destroy()
        return resultado
    except Exception:
        seleccionados: Dict[str, Tuple[str, float, float]] = {}
        for raw in faltantes:
            nombre = raw.get("nombre_producto") or raw.get("producto") or ""
            accion = (
                input(
                    f"Materia prima '{nombre}' no encontrada. ¿Crear u omitir? (crear/omitir): "
                )
                .strip()
                .lower()
            )
            if accion != "crear":
                continue
            unidad = input(f"Unidad de medida para '{nombre}': ").strip()
            costo = float(input(f"Costo unitario para '{nombre}': "))
            stock = float(input(f"Stock inicial para '{nombre}': "))
            seleccionados[nombre] = (unidad, costo, stock)
        return seleccionados

