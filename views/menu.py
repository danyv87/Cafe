from controllers.productos_controller import agregar_producto, listar_productos
# Actualiza las importaciones para usar los nuevos nombres de funciones del controlador de tickets
from controllers.tickets_controller import registrar_ticket, listar_tickets, total_vendido_tickets
# Importa VentaDetalle para usarlo en menu_ventas
from models.venta_detalle import VentaDetalle


def mostrar_menu_principal():
    print("\n📋 MENÚ PRINCIPAL")
    print("1. Gestionar productos")
    print("2. Registrar venta")
    print("3. Ver historial e informes")
    print("4. Salir")
    return input("Seleccione una opción: ")


# ------------------------ PRODUCTOS ------------------------

def menu_productos():
    while True:
        print("\n🛒 GESTIÓN DE PRODUCTOS")
        print("1. Listar productos")
        print("2. Agregar nuevo producto")
        print("3. Volver al menú principal")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            productos = listar_productos()
            if not productos:
                print("No hay productos registrados.")
            else:
                print("\nProductos disponibles:")
                for p in productos:
                    print(f"🔹 {p.nombre} - ${p.precio_unitario:.2f} (ID: {p.id})")
        elif opcion == "2":
            nombre = input("Nombre del producto: ")
            try:
                precio = float(input("Precio unitario: "))
                producto = agregar_producto(nombre, precio)
                print(f"✅ Producto agregado: {producto.nombre} (${producto.precio_unitario:.2f})")
            except ValueError:
                print("❌ Precio inválido.")
        elif opcion == "3":
            break
        else:
            print("Opción inválida. Intente nuevamente.")


# ------------------------ VENTAS (Ahora para tickets) ------------------------

def menu_ventas():
    productos = listar_productos()
    if not productos:
        print("⚠️ No hay productos cargados. Agregue al menos uno primero.")
        return

    print("\n🧾 REGISTRAR VENTA (Ticket)")

    # Lista para almacenar los ítems de la venta actual (VentaDetalle)
    items_para_ticket = []
    cliente_nombre = input("Nombre del Cliente para el ticket: ").strip()
    if not cliente_nombre:
        print("❌ El nombre del cliente no puede estar vacío.")
        return

    while True:
        print("\n--- Añadir Producto al Ticket ---")
        for idx, p in enumerate(productos, start=1):
            print(f"{idx}. {p.nombre} - ${p.precio_unitario:.2f}")
        print("0. Terminar y Generar Ticket")

        try:
            seleccion = int(input("Seleccione un producto (número) o '0' para finalizar: "))
            if seleccion == 0:
                break  # Sale del bucle para generar el ticket

            if seleccion < 1 or seleccion > len(productos):
                raise ValueError

            producto_seleccionado = productos[seleccion - 1]
            cantidad = int(input(f"Cantidad de '{producto_seleccionado.nombre}': "))
            if cantidad <= 0:
                raise ValueError

            # Crea un objeto VentaDetalle para este ítem
            detalle = VentaDetalle(
                producto_id=producto_seleccionado.id,
                nombre_producto=producto_seleccionado.nombre,
                cantidad=cantidad,
                precio_unitario=producto_seleccionado.precio_unitario
            )
            items_para_ticket.append(detalle)
            print(f"✅ '{cantidad} x {producto_seleccionado.nombre}' añadido al ticket.")

        except ValueError:
            print("❌ Entrada inválida. Por favor, ingrese un número válido para la selección o cantidad.")
        except Exception as e:
            print(f"❌ Ocurrió un error inesperado al añadir producto: {e}")

    if not items_para_ticket:
        print("⚠️ No se añadieron productos al ticket. Venta cancelada.")
        return

    try:
        # Llama a la nueva función registrar_ticket del controlador
        ticket_generado = registrar_ticket(cliente_nombre, items_para_ticket)
        print(f"\n✅ Ticket generado para '{ticket_generado.cliente}' (ID: {ticket_generado.id[:8]}...).")
        print(f"   Total del Ticket: ${ticket_generado.total:.2f}")
        print("   Productos en el ticket:")
        for item in ticket_generado.items_venta:
            print(f"     - {item.cantidad} x {item.nombre_producto} @ ${item.precio_unitario:.2f} = ${item.total:.2f}")

    except ValueError as e:
        print(f"❌ Error al generar el ticket: {e}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al generar el ticket: {e}")


# ------------------------ INFORMES (Ahora para tickets) ------------------------

def menu_informes():
    print("\n📊 HISTORIAL DE VENTAS (Tickets)")
    # Usa la nueva función listar_tickets
    tickets = listar_tickets()
    if not tickets:
        print("No hay tickets registrados.")
        return

    for t in tickets:
        print(f"\n--- Ticket ID: {t.id[:8]}... ---")
        print(f"Fecha: {t.fecha}")
        print(f"Cliente: {t.cliente}")
        print("Productos:")
        for item in t.items_venta:
            print(f"  - {item.cantidad} x {item.nombre_producto} @ ${item.precio_unitario:.2f} = ${item.total:.2f}")
        print(f"Total del Ticket: ${t.total:.2f}")

    # Usa la nueva función total_vendido_tickets
    print(f"\n💰 Total vendido (todos los tickets): ${total_vendido_tickets():.2f}")
