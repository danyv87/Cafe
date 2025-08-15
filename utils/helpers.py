import argparse
import os
import shutil

from views.menu import mostrar_menu_principal

BACKUP_DIR = os.path.join("data", "backups")


def listar_backups():
    """Mostrar los archivos de respaldo disponibles."""
    if not os.path.exists(BACKUP_DIR):
        print("No hay backups disponibles.")
        return
    archivos = sorted(f for f in os.listdir(BACKUP_DIR) if f.endswith(".json"))
    for nombre in archivos:
        print(nombre)


def restaurar_backup(nombre_archivo, destino=None):
    """Restaurar el *nombre_archivo* desde el directorio de backups."""
    src = os.path.join(BACKUP_DIR, nombre_archivo)
    if not os.path.exists(src):
        print(f"Backup {nombre_archivo} no encontrado.")
        return
    if destino is None:
        base = nombre_archivo.split("-", 1)[0] + ".json"
        destino = os.path.join("data", base)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copy(src, destino)
    print(f"Backup {nombre_archivo} restaurado en {destino}")


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
    parser = argparse.ArgumentParser(description="Utilidades de la cafetería")
    parser.add_argument("--listar-backups", action="store_true", help="Listar archivos de respaldo")
    parser.add_argument("--restaurar", metavar="NOMBRE", help="Restaurar backup indicado")
    parser.add_argument("--destino", help="Ruta destino para restaurar")
    args = parser.parse_args()

    if args.listar_backups:
        listar_backups()
    elif args.restaurar:
        restaurar_backup(args.restaurar, args.destino)
    else:
        main()
