# main.py
# Este archivo es el punto de entrada principal de la aplicación.

# Importa la función para iniciar la aplicación GUI.
import logging
from gui.app import iniciar_app


def main() -> None:
    """Configuración de logging y arranque de la aplicación."""
    logging.basicConfig(level=logging.INFO)
    iniciar_app()


if __name__ == "__main__":
    main()

