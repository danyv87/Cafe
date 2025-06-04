from views.menu import mostrar_menu_principal


def main():
    while True:
        opcion = mostrar_menu_principal()

        if opcion == "1":
            from views.menu import menu_productos
            menu_productos()
        elif opcion == "2":
            from views.menu import menu_ventas
            menu_ventas()
        elif opcion == "3":
            from views.menu import menu_informes
            menu_informes()
        elif opcion == "4":
            print("Gracias por usar el sistema de ventas de la cafetería. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    main()
