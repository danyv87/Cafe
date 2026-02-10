from datetime import datetime
import tkinter as tk
from tkinter import ttk

from controllers.compras_controller import listar_compras
from controllers.gastos_adicionales_controller import listar_gastos_adicionales
from controllers.productos_controller import obtener_rentabilidad_productos
from controllers.tickets_controller import listar_tickets


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _formatear_moneda(valor: float) -> str:
    return f"Gs {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _parse_fecha(fecha):
    if isinstance(fecha, datetime):
        return fecha
    if isinstance(fecha, str):
        fecha = fecha[:19]
        for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(fecha, formato)
            except ValueError:
                continue
    return None


def _inicio_mes(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _mes_anterior(dt: datetime) -> datetime:
    if dt.month == 1:
        return dt.replace(year=dt.year - 1, month=12)
    return dt.replace(month=dt.month - 1)


def _nombre_periodo(dt: datetime) -> str:
    return f"{MESES[dt.month - 1]} {dt.year}"


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
    ttk.Label(item_frame, text=f"Margen: {margen} | Ventas: {ventas}", font=("Helvetica", 10)).pack(anchor="w")
    item_frame.pack(fill=tk.X, pady=4)


def _periodos_disponibles(tickets, compras, gastos):
    periodos = set()

    for ticket in tickets:
        fecha = _parse_fecha(ticket.fecha)
        if fecha:
            periodos.add((fecha.year, fecha.month))

    for compra in compras:
        fecha = _parse_fecha(compra.fecha)
        if fecha:
            periodos.add((fecha.year, fecha.month))

    for gasto in gastos:
        fecha = _parse_fecha(gasto.fecha)
        if fecha:
            periodos.add((fecha.year, fecha.month))

    now = datetime.now()
    periodos.add((now.year, now.month))
    return sorted(periodos)


def _obtener_datos_dashboard(periodo_actual: datetime, tickets, compras, gastos, rentabilidad) -> dict:
    periodo_anterior = _inicio_mes(_mes_anterior(periodo_actual))
    margenes = {item["producto_id"]: item["margen_beneficio"] for item in rentabilidad}

    ventas_actual = 0.0
    ventas_anterior = 0.0
    tickets_mes = []
    ventas_por_producto = {}
    unidades_vendidas = 0

    for ticket in tickets:
        fecha = _parse_fecha(ticket.fecha)
        if not fecha:
            continue
        mes_ticket = _inicio_mes(fecha)
        if mes_ticket == periodo_actual:
            tickets_mes.append(ticket)
            ventas_actual += ticket.total
            for item in ticket.items_venta:
                unidades_vendidas += item.cantidad
                if item.producto_id not in ventas_por_producto:
                    ventas_por_producto[item.producto_id] = {"nombre": item.nombre_producto, "ventas": 0.0}
                ventas_por_producto[item.producto_id]["ventas"] += item.total
        elif mes_ticket == periodo_anterior:
            ventas_anterior += ticket.total

    compras_actual = 0.0
    compras_anterior = 0.0
    compras_mes_actual = []
    compras_mes_anterior = []

    for compra in compras:
        fecha = _parse_fecha(compra.fecha)
        if not fecha:
            continue
        mes_compra = _inicio_mes(fecha)
        if mes_compra == periodo_actual:
            compras_mes_actual.append(compra)
            compras_actual += compra.total
        elif mes_compra == periodo_anterior:
            compras_mes_anterior.append(compra)
            compras_anterior += compra.total

    gastos_actual = 0.0
    gastos_anterior = 0.0
    gastos_mes_actual = []

    for gasto in gastos:
        fecha = _parse_fecha(gasto.fecha)
        if not fecha:
            continue
        mes_gasto = _inicio_mes(fecha)
        if mes_gasto == periodo_actual:
            gastos_mes_actual.append(gasto)
            gastos_actual += gasto.monto
        elif mes_gasto == periodo_anterior:
            gastos_anterior += gasto.monto

    resultado_actual = ventas_actual - compras_actual - gastos_actual
    resultado_anterior = ventas_anterior - compras_anterior - gastos_anterior

    variacion_resultado = None
    if resultado_anterior != 0:
        variacion_resultado = ((resultado_actual - resultado_anterior) / abs(resultado_anterior)) * 100

    margen_promedio = (resultado_actual / ventas_actual * 100) if ventas_actual > 0 else 0.0

    contribucion_ponderada = 0.0
    for producto_id, info in ventas_por_producto.items():
        margen = margenes.get(producto_id)
        if margen is not None:
            contribucion_ponderada += info["ventas"] * (margen / 100)

    ratio_contribucion = (contribucion_ponderada / ventas_actual) if ventas_actual > 0 else 0.0
    punto_equilibrio = (gastos_actual / ratio_contribucion) if ratio_contribucion > 0 else 0.0

    dias_operativos = len({
        _parse_fecha(t.fecha).date()
        for t in tickets_mes
        if _parse_fecha(t.fecha)
    })
    ticket_promedio = ventas_actual / len(tickets_mes) if tickets_mes else 0.0
    ventas_diarias = ventas_actual / dias_operativos if dias_operativos else 0.0

    productos_ranking = []
    for producto_id, info in ventas_por_producto.items():
        productos_ranking.append({
            "nombre": info["nombre"],
            "margen": margenes.get(producto_id, 0.0),
            "ventas": info["ventas"],
        })

    top_estrella = sorted(productos_ranking, key=lambda x: (x["margen"], x["ventas"]), reverse=True)[:3]
    top_problema = sorted(productos_ranking, key=lambda x: (x["margen"], -x["ventas"]))[:3]

    alertas = []
    producto_perdida = next((p for p in top_problema if p["margen"] < 0), None)
    if producto_perdida:
        alertas.append(f"🔴 {producto_perdida['nombre']} tiene margen negativo ({producto_perdida['margen']:.1f}%).")

    total_alquiler = sum(g.monto for g in gastos_mes_actual if "alquiler" in g.nombre.lower())
    if gastos_actual > 0 and total_alquiler > 0:
        share_alquiler = (total_alquiler / gastos_actual) * 100
        estado = "alto" if share_alquiler >= 35 else "controlado"
        alertas.append(f"🟡 El alquiler representa {share_alquiler:.0f}% de los costos fijos ({estado}).")

    def _precio_promedio_cafe(compras_mes):
        total = 0.0
        cantidad = 0.0
        for compra in compras_mes:
            for item in compra.items_compra:
                nombre = (item.nombre_producto or "").lower()
                descripcion = (item.descripcion_adicional or "").lower()
                if "café" in nombre or "cafe" in nombre or "café" in descripcion or "cafe" in descripcion:
                    total += item.costo_unitario * item.cantidad
                    cantidad += item.cantidad
        return (total / cantidad) if cantidad > 0 else None

    cafe_actual = _precio_promedio_cafe(compras_mes_actual)
    cafe_anterior = _precio_promedio_cafe(compras_mes_anterior)
    if cafe_actual is not None and cafe_anterior not in (None, 0):
        variacion_cafe = ((cafe_actual - cafe_anterior) / cafe_anterior) * 100
        if abs(variacion_cafe) >= 5:
            icono = "🟡" if variacion_cafe > 0 else "🟢"
            verbo = "subió" if variacion_cafe > 0 else "bajó"
            alertas.append(f"{icono} El café molido {verbo} {abs(variacion_cafe):.0f}% este mes.")

    if not alertas:
        alertas.append("🟢 Sin alertas críticas este período.")

    return {
        "periodo": _nombre_periodo(periodo_actual),
        "resultado_actual": resultado_actual,
        "variacion_resultado": variacion_resultado,
        "margen_promedio": margen_promedio,
        "ventas_actual": ventas_actual,
        "punto_equilibrio": punto_equilibrio,
        "faltante_pe": max(punto_equilibrio - ventas_actual, 0.0),
        "unidades_vendidas": unidades_vendidas,
        "ticket_promedio": ticket_promedio,
        "ventas_diarias": ventas_diarias,
        "dias_operativos": dias_operativos,
        "top_estrella": top_estrella,
        "top_problema": top_problema,
        "alertas": alertas,
    }


def _render_dashboard(content_frame: ttk.Frame, datos: dict) -> None:
    for child in content_frame.winfo_children():
        child.destroy()

    ttk.Label(content_frame, text="📊 Dashboard Ejecutivo — Cafetería", font=("Helvetica", 18, "bold")).pack(anchor="w")
    ttk.Label(content_frame, text=f"Período: {datos['periodo']}", font=("Helvetica", 11)).pack(anchor="w", pady=(2, 12))

    ttk.Label(content_frame, text="🟢 Estado General (vista en 5 segundos)", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(0, 8))

    tarjetas_frame = ttk.Frame(content_frame)
    tarjetas_frame.pack(fill=tk.BOTH, expand=True)

    color_resultado = "#1B5E20" if datos["resultado_actual"] >= 0 else "#B71C1C"
    icono_resultado = "🟢" if datos["resultado_actual"] >= 0 else "🔴"

    variacion = datos["variacion_resultado"]
    if variacion is None:
        detalle_resultado = "Sin base comparativa del mes anterior"
    else:
        flecha = "⬆️" if variacion >= 0 else "⬇️"
        detalle_resultado = f"{flecha} {variacion:+.0f}% vs mes anterior"

    _crear_tarjeta(
        tarjetas_frame,
        "Resultado del mes",
        f"{icono_resultado} {_formatear_moneda(datos['resultado_actual'])}",
        detalle_resultado,
        color_resultado,
    )
    _crear_tarjeta(
        tarjetas_frame,
        "Margen promedio",
        ("🟢" if datos["margen_promedio"] >= 45 else "🟡") + f" {datos['margen_promedio']:.1f}%",
        "Objetivo ≥ 45%",
        "#1B5E20" if datos["margen_promedio"] >= 45 else "#B26A00",
    )
    _crear_tarjeta(
        tarjetas_frame,
        "Ventas totales",
        _formatear_moneda(datos["ventas_actual"]),
        "Mes seleccionado",
        "#0D47A1",
    )
    _crear_tarjeta(
        tarjetas_frame,
        "Punto de equilibrio",
        "🔴 " + _formatear_moneda(datos["punto_equilibrio"]),
        "📉 Falta cubrir: " + _formatear_moneda(datos["faltante_pe"]),
        "#B71C1C" if datos["faltante_pe"] > 0 else "#1B5E20",
    )

    ttk.Label(content_frame, text="📈 Ventas y eficiencia", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(15, 6))

    tree = ttk.Treeview(content_frame, columns=("Indicador", "Valor", "Estado"), show="headings", height=5)
    tree.heading("Indicador", text="Indicador")
    tree.heading("Valor", text="Valor")
    tree.heading("Estado", text="Estado")
    tree.column("Indicador", width=220)
    tree.column("Valor", width=180, anchor="center")
    tree.column("Estado", width=100, anchor="center")
    tree.pack(fill=tk.X, padx=2)

    indicadores = [
        ("Unidades vendidas", f"{datos['unidades_vendidas']:,}".replace(",", "."), "🟢" if datos["unidades_vendidas"] > 0 else "⚪"),
        ("Ticket promedio", _formatear_moneda(datos["ticket_promedio"]), "🟢" if datos["ticket_promedio"] >= 10000 else "🟡 Bajo"),
        ("Ventas diarias promedio", _formatear_moneda(datos["ventas_diarias"]), "🟢" if datos["ventas_diarias"] > 0 else "⚪"),
        ("Días operativos", str(datos["dias_operativos"]), "🟢" if datos["dias_operativos"] >= 20 else "🟡"),
    ]
    for fila in indicadores:
        tree.insert("", tk.END, values=fila)

    ttk.Label(content_frame, text="💡 Indicadores calculados con los datos cargados del sistema.", font=("Helvetica", 10, "italic")).pack(anchor="w", pady=(6, 12))

    ttk.Label(content_frame, text="⭐ Productos clave", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(5, 6))

    productos_frame = ttk.Frame(content_frame)
    productos_frame.pack(fill=tk.BOTH, expand=True)

    top_frame = ttk.LabelFrame(productos_frame, text="🟢 Top 3 — Productos estrella", padding=10)
    top_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

    if datos["top_estrella"]:
        for item in datos["top_estrella"]:
            _crear_item_producto(top_frame, item["nombre"], f"{item['margen']:.1f}%", _formatear_moneda(item["ventas"]), "#1B5E20")
    else:
        ttk.Label(top_frame, text="Sin ventas en el período.", font=("Helvetica", 10, "italic")).pack(anchor="w")

    problema_frame = ttk.LabelFrame(productos_frame, text="🔴 Top 3 — Productos problema", padding=10)
    problema_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

    if datos["top_problema"]:
        for item in datos["top_problema"]:
            _crear_item_producto(problema_frame, item["nombre"], f"{item['margen']:.1f}%", _formatear_moneda(item["ventas"]), "#B71C1C")
    else:
        ttk.Label(problema_frame, text="Sin ventas en el período.", font=("Helvetica", 10, "italic")).pack(anchor="w")

    ttk.Label(content_frame, text="⚠️ Los productos problema tienen menor margen relativo.", font=("Helvetica", 10, "italic")).pack(anchor="w", pady=(8, 14))

    ttk.Label(content_frame, text="🚨 Alertas gerenciales", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(5, 6))
    for alerta in datos["alertas"]:
        ttk.Label(content_frame, text=alerta, font=("Helvetica", 11)).pack(anchor="w", pady=2)


def agregar_tab_dashboard_ejecutivo(notebook: ttk.Notebook) -> None:
    tickets = listar_tickets()
    compras = listar_compras()
    gastos = listar_gastos_adicionales()
    rentabilidad = obtener_rentabilidad_productos()

    periodos = _periodos_disponibles(tickets, compras, gastos)

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Dashboard Ejecutivo")

    style = ttk.Style()
    style.configure("Card.TFrame", relief="solid", borderwidth=1)

    selector_frame = ttk.Frame(frame, padding=(12, 8))
    selector_frame.pack(fill=tk.X)

    ttk.Label(selector_frame, text="Año:").pack(side=tk.LEFT, padx=(0, 6))
    year_values = sorted({str(y) for y, _ in periodos})
    selected_year = tk.StringVar(value=str(periodos[-1][0]))
    cb_year = ttk.Combobox(selector_frame, state="readonly", values=year_values, width=8, textvariable=selected_year)
    cb_year.pack(side=tk.LEFT, padx=(0, 12))

    ttk.Label(selector_frame, text="Mes:").pack(side=tk.LEFT, padx=(0, 6))
    selected_month = tk.StringVar(value=str(periodos[-1][1]))
    cb_month = ttk.Combobox(selector_frame, state="readonly", width=10, textvariable=selected_month)
    cb_month.pack(side=tk.LEFT)

    main_canvas = tk.Canvas(frame)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_main = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=main_canvas.yview)
    scrollbar_main.pack(side=tk.RIGHT, fill=tk.Y)

    main_canvas.configure(yscrollcommand=scrollbar_main.set)
    main_canvas.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

    content_frame = ttk.Frame(main_canvas, padding=15)
    main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def _meses_de_anio(anio: str):
        meses = sorted({m for y, m in periodos if str(y) == anio})
        return [str(m) for m in meses]

    def _actualizar_dashboard(_event=None):
        anio = int(selected_year.get())
        mes = int(selected_month.get())
        datos = _obtener_datos_dashboard(
            datetime(anio, mes, 1),
            tickets,
            compras,
            gastos,
            rentabilidad,
        )
        _render_dashboard(content_frame, datos)
        content_frame.update_idletasks()
        main_canvas.config(scrollregion=main_canvas.bbox("all"))

    def _actualizar_meses(_event=None):
        meses = _meses_de_anio(selected_year.get())
        cb_month["values"] = meses
        if selected_month.get() not in meses:
            selected_month.set(meses[-1])
        _actualizar_dashboard()

    cb_year.bind("<<ComboboxSelected>>", _actualizar_meses)
    cb_month.bind("<<ComboboxSelected>>", _actualizar_dashboard)

    cb_month["values"] = _meses_de_anio(selected_year.get())
    _actualizar_dashboard()
