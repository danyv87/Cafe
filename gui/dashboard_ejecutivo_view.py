import tkinter as tk
from tkinter import ttk

from controllers.dashboard_controller import (
    calcular_metricas_dashboard_mensual,
    meses_disponibles_dashboard,
)
from controllers.productos_controller import obtener_producto_por_id


def _formatear_moneda(valor: float) -> str:
    return f"Gs {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _nombre_producto(producto_id: str) -> str:
    producto = obtener_producto_por_id(producto_id)
    if producto:
        return producto.nombre
    return producto_id


def agregar_tab_dashboard_ejecutivo(notebook: ttk.Notebook) -> None:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Dashboard Ejecutivo")

    meses = meses_disponibles_dashboard()

    selector_frame = ttk.Frame(frame, padding=(15, 10))
    selector_frame.pack(fill=tk.X)

    ttk.Label(
        selector_frame,
        text="Mes de interés:",
        font=("Helvetica", 11, "bold"),
    ).pack(side=tk.LEFT)

    mes_var = tk.StringVar(value=meses[-1] if meses else "")
    combo_meses = ttk.Combobox(
        selector_frame,
        textvariable=mes_var,
        state="readonly",
        values=meses,
        width=12,
    )
    combo_meses.pack(side=tk.LEFT, padx=(8, 0))

    mensaje_var = tk.StringVar(value="")
    ttk.Label(selector_frame, textvariable=mensaje_var, foreground="#B26A00").pack(
        side=tk.LEFT, padx=(12, 0)
    )

    contenido = ttk.Frame(frame, padding=15)
    contenido.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        contenido,
        text="📊 Dashboard Ejecutivo — Cafetería",
        font=("Helvetica", 18, "bold"),
    ).pack(anchor="w")

    periodo_var = tk.StringVar(value="")
    ttk.Label(contenido, textvariable=periodo_var, font=("Helvetica", 11)).pack(
        anchor="w", pady=(2, 12)
    )

    ttk.Label(
        contenido,
        text="🟢 Estado General",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(0, 8))

    tarjetas_frame = ttk.Frame(contenido)
    tarjetas_frame.pack(fill=tk.X)

    cards = {}
    definiciones = [
        ("resultado", "Resultado del mes", "#1B5E20"),
        ("margen", "Margen promedio", "#B26A00"),
        ("ventas", "Ventas totales", "#0D47A1"),
        ("equilibrio", "Punto de equilibrio", "#B71C1C"),
    ]
    for clave, titulo, color in definiciones:
        card = ttk.Frame(tarjetas_frame, padding=10, relief="solid", borderwidth=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(card, text=titulo, font=("Helvetica", 11, "bold")).pack(anchor="w")
        valor_var = tk.StringVar(value="-")
        detalle_var = tk.StringVar(value="-")
        ttk.Label(card, textvariable=valor_var, font=("Helvetica", 16, "bold"), foreground=color).pack(
            anchor="w", pady=2
        )
        ttk.Label(card, textvariable=detalle_var, font=("Helvetica", 10)).pack(anchor="w")
        cards[clave] = (valor_var, detalle_var)

    ttk.Label(
        contenido,
        text="📈 Ventas y eficiencia",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(15, 6))

    tree = ttk.Treeview(contenido, columns=("Indicador", "Valor", "Estado"), show="headings", height=4)
    tree.heading("Indicador", text="Indicador")
    tree.heading("Valor", text="Valor")
    tree.heading("Estado", text="Estado")
    tree.column("Indicador", width=220)
    tree.column("Valor", width=140, anchor="center")
    tree.column("Estado", width=120, anchor="center")
    tree.pack(fill=tk.X, padx=2)

    insight_var = tk.StringVar(value="")
    ttk.Label(contenido, textvariable=insight_var, font=("Helvetica", 10, "italic")).pack(
        anchor="w", pady=(6, 12)
    )

    ttk.Label(
        contenido,
        text="⭐ Productos clave",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(5, 6))

    productos_frame = ttk.Frame(contenido)
    productos_frame.pack(fill=tk.BOTH, expand=True)
    productos_frame.columnconfigure(0, weight=1)
    productos_frame.columnconfigure(1, weight=1)

    top_frame = ttk.LabelFrame(productos_frame, text="🟢 Top 3 — Productos estrella", padding=10)
    top_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    problema_frame = ttk.LabelFrame(productos_frame, text="🔴 Top 3 — Productos problema", padding=10)
    problema_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    def _render_productos(frame_obj: ttk.LabelFrame, datos: list[dict], vacio_msg: str, color: str) -> None:
        for child in frame_obj.winfo_children():
            child.destroy()

        if not datos:
            ttk.Label(frame_obj, text=vacio_msg, font=("Helvetica", 10, "italic")).pack(anchor="w")
            return

        for prod in datos:
            nombre = _nombre_producto(prod["producto_id"])
            margen = f"{prod['margen_pct']:.1f} %"
            ventas = _formatear_moneda(prod["ventas"])
            ttk.Label(frame_obj, text=nombre, font=("Helvetica", 11, "bold"), foreground=color).pack(anchor="w")
            ttk.Label(
                frame_obj,
                text=f"Margen: {margen} | Ventas: {ventas} | Unidades: {prod['unidades']}",
                font=("Helvetica", 10),
            ).pack(anchor="w", pady=(0, 6))

    def _cargar_mes(*_: object) -> None:
        mes = mes_var.get()
        if not mes:
            mensaje_var.set("No hay meses con datos para mostrar.")
            return

        metricas = calcular_metricas_dashboard_mensual(mes)
        periodo_var.set(f"Período: {mes}")
        mensaje_var.set("")

        cards["resultado"][0].set(_formatear_moneda(metricas.resultado_mes))
        if metricas.ventas_totales > 0:
            margen_promedio = (metricas.resultado_mes / metricas.ventas_totales) * 100
        else:
            margen_promedio = 0.0
        cards["margen"][0].set(f"{margen_promedio:.1f} %")
        cards["ventas"][0].set(_formatear_moneda(metricas.ventas_totales))
        cards["equilibrio"][0].set(_formatear_moneda(metricas.punto_equilibrio))

        cards["resultado"][1].set(f"Costos + gastos: {_formatear_moneda(metricas.costos_produccion + metricas.gastos_adicionales)}")
        cards["margen"][1].set(f"Costos producción: {_formatear_moneda(metricas.costos_produccion)}")
        cards["ventas"][1].set("Mes seleccionado")

        faltante = max(metricas.punto_equilibrio - metricas.ventas_totales, 0)
        if faltante > 0:
            cards["equilibrio"][1].set(f"Falta cubrir: {_formatear_moneda(faltante)}")
        else:
            cards["equilibrio"][1].set("Objetivo cubierto")

        for row in tree.get_children():
            tree.delete(row)

        estado_ticket = "🟢" if metricas.ticket_promedio > 0 else "⚪"
        estado_diario = "🟢" if metricas.ventas_diarias_promedio > 0 else "⚪"

        indicadores = [
            ("Unidades vendidas", f"{metricas.unidades_vendidas}", "🟢" if metricas.unidades_vendidas > 0 else "⚪"),
            ("Ticket promedio", _formatear_moneda(metricas.ticket_promedio), estado_ticket),
            ("Ventas diarias promedio", _formatear_moneda(metricas.ventas_diarias_promedio), estado_diario),
            ("Días operativos", f"{metricas.dias_operativos}", "🟢" if metricas.dias_operativos > 0 else "⚪"),
        ]
        for fila in indicadores:
            tree.insert("", tk.END, values=fila)

        if metricas.unidades_vendidas == 0:
            insight_var.set("💡 No hubo ventas en el mes seleccionado.")
        elif margen_promedio < 20:
            insight_var.set("💡 Hay ventas, pero el margen del mes es bajo.")
        else:
            insight_var.set("💡 Buen volumen con rentabilidad aceptable en el mes.")

        _render_productos(top_frame, metricas.top_productos, "Sin productos vendidos en este mes.", "#1B5E20")
        _render_productos(
            problema_frame,
            metricas.productos_problema,
            "Sin datos suficientes para detectar productos problema.",
            "#B71C1C",
        )

    combo_meses.bind("<<ComboboxSelected>>", _cargar_mes)
    _cargar_mes()
