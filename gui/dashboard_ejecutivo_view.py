import tkinter as tk
from tkinter import ttk


def _formatear_moneda(valor: float) -> str:
    return f"Gs {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _crear_tarjeta(parent: tk.Widget, titulo: str, valor: str, detalle: str, color: str) -> None:
    tarjeta = ttk.Frame(parent, padding=10)
    tarjeta.configure(style="Card.TFrame")
    ttk.Label(tarjeta, text=titulo, font=("Helvetica", 11, "bold")).pack(anchor="w")
    ttk.Label(tarjeta, text=valor, font=("Helvetica", 16, "bold"), foreground=color).pack(anchor="w", pady=2)
    ttk.Label(tarjeta, text=detalle, font=("Helvetica", 10)).pack(anchor="w")
    tarjeta.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)


def _crear_item_producto(parent: tk.Widget, nombre: str, margen: str, ventas: str, color: str) -> None:
    item_frame = ttk.Frame(parent, padding=(0, 4))
    ttk.Label(item_frame, text=nombre, font=("Helvetica", 11, "bold"), foreground=color).pack(anchor="w")
    ttk.Label(
        item_frame,
        text=f"Margen: {margen} | Ventas: {ventas}",
        font=("Helvetica", 10),
    ).pack(anchor="w")
    item_frame.pack(fill=tk.X, pady=4)


def agregar_tab_dashboard_ejecutivo(notebook: ttk.Notebook) -> None:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Dashboard Ejecutivo")

    style = ttk.Style()
    style.configure("Card.TFrame", relief="solid", borderwidth=1)

    main_canvas = tk.Canvas(frame, highlightthickness=0)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_main = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=main_canvas.yview)
    scrollbar_main.pack(side=tk.RIGHT, fill=tk.Y)

    main_canvas.configure(yscrollcommand=scrollbar_main.set)

    content_frame = ttk.Frame(main_canvas, padding=15)
    content_window = main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def _actualizar_region_scroll(_: tk.Event | None = None) -> None:
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    def _ajustar_ancho_contenido(event: tk.Event) -> None:
        main_canvas.itemconfigure(content_window, width=event.width)

    def _scroll_con_rueda(event: tk.Event) -> str:
        if event.delta:
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            paso = -1 if event.num == 4 else 1
            main_canvas.yview_scroll(paso, "units")
        return "break"

    def _activar_scroll(_: tk.Event | None = None) -> None:
        main_canvas.bind_all("<MouseWheel>", _scroll_con_rueda)
        main_canvas.bind_all("<Button-4>", _scroll_con_rueda)
        main_canvas.bind_all("<Button-5>", _scroll_con_rueda)

    def _desactivar_scroll(_: tk.Event | None = None) -> None:
        main_canvas.unbind_all("<MouseWheel>")
        main_canvas.unbind_all("<Button-4>")
        main_canvas.unbind_all("<Button-5>")

    main_canvas.bind("<Configure>", _ajustar_ancho_contenido)
    content_frame.bind("<Configure>", _actualizar_region_scroll)
    main_canvas.bind("<Enter>", _activar_scroll)
    main_canvas.bind("<Leave>", _desactivar_scroll)

    ttk.Label(
        content_frame,
        text="📊 Dashboard Ejecutivo — Cafetería",
        font=("Helvetica", 18, "bold"),
    ).pack(anchor="w")
    ttk.Label(content_frame, text="Período: Febrero 2026", font=("Helvetica", 11)).pack(anchor="w", pady=(2, 12))

    ttk.Label(
        content_frame,
        text="🟢 Estado General (vista en 5 segundos)",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(0, 8))

    tarjetas_frame = ttk.Frame(content_frame)
    tarjetas_frame.pack(fill=tk.BOTH, expand=True)

    _crear_tarjeta(
        tarjetas_frame,
        "Resultado del mes",
        f"🟢 {_formatear_moneda(3_250_000)}",
        "⬆️ +12 % vs mes anterior",
        "#1B5E20",
    )
    _crear_tarjeta(
        tarjetas_frame,
        "Margen promedio",
        "🟡 41 %",
        "Objetivo ≥ 45 %",
        "#B26A00",
    )
    _crear_tarjeta(
        tarjetas_frame,
        "Ventas totales",
        _formatear_moneda(7_300_000),
        "Mes actual",
        "#0D47A1",
    )
    _crear_tarjeta(
        tarjetas_frame,
        "Punto de equilibrio",
        "🔴 " + _formatear_moneda(8_900_000),
        "📉 Falta cubrir: " + _formatear_moneda(1_600_000),
        "#B71C1C",
    )

    ttk.Label(
        content_frame,
        text="📈 Ventas y eficiencia",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(15, 6))

    tree = ttk.Treeview(content_frame, columns=("Indicador", "Valor", "Estado"), show="headings", height=5)
    tree.heading("Indicador", text="Indicador")
    tree.heading("Valor", text="Valor")
    tree.heading("Estado", text="Estado")
    tree.column("Indicador", width=220)
    tree.column("Valor", width=140, anchor="center")
    tree.column("Estado", width=80, anchor="center")
    tree.pack(fill=tk.X, padx=2)

    indicadores = [
        ("Unidades vendidas", "2.140", "🟢"),
        ("Ticket promedio", _formatear_moneda(3_410), "🟡 Bajo"),
        ("Ventas diarias promedio", _formatear_moneda(243_000), "🟡"),
        ("Días operativos", "30", "🟢"),
    ]
    for fila in indicadores:
        tree.insert("", tk.END, values=fila)

    ttk.Label(
        content_frame,
        text="💡 Se vende bien en volumen, pero con ticket bajo.",
        font=("Helvetica", 10, "italic"),
    ).pack(anchor="w", pady=(6, 12))

    ttk.Label(
        content_frame,
        text="⭐ Productos clave",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(5, 6))

    productos_frame = ttk.Frame(content_frame)
    productos_frame.pack(fill=tk.BOTH, expand=True)
    productos_frame.columnconfigure(0, weight=1)
    productos_frame.columnconfigure(1, weight=1)

    top_frame = ttk.LabelFrame(productos_frame, text="🟢 Top 3 — Productos estrella", padding=10)
    top_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    _crear_item_producto(top_frame, "☕ Latte grande", "62 %", _formatear_moneda(1_120_000), "#1B5E20")
    _crear_item_producto(top_frame, "🧁 Muffin chocolate", "55 %", _formatear_moneda(840_000), "#1B5E20")
    _crear_item_producto(top_frame, "☕ Capuccino", "51 %", _formatear_moneda(960_000), "#1B5E20")

    problema_frame = ttk.LabelFrame(productos_frame, text="🔴 Top 3 — Productos problema", padding=10)
    problema_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    _crear_item_producto(problema_frame, "🥐 Medialuna rellena", "−4 %", _formatear_moneda(390_000), "#B71C1C")
    _crear_item_producto(problema_frame, "🧊 Frappé", "8 %", _formatear_moneda(510_000), "#B71C1C")
    _crear_item_producto(problema_frame, "🥪 Sándwich veggie", "12 %", _formatear_moneda(470_000), "#B71C1C")

    ttk.Label(
        content_frame,
        text="⚠️ Estos productos venden, pero pierden rentabilidad.",
        font=("Helvetica", 10, "italic"),
    ).pack(anchor="w", pady=(8, 14))

    ttk.Label(
        content_frame,
        text="🚨 Alertas gerenciales",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=(5, 6))

    alertas = [
        "🔴 La medialuna rellena pierde dinero.",
        "🟡 El alquiler representa el 38 % de los costos fijos (alto).",
        "🟡 El café molido subió 14 % este mes.",
    ]
    for alerta in alertas:
        ttk.Label(content_frame, text=alerta, font=("Helvetica", 11)).pack(anchor="w", pady=2)

    _vincular_scroll(main_canvas)

    content_frame.update_idletasks()
    _actualizar_region_scroll()
