# Cafe Management System

This project is a simple GUI-based application for managing a cafe. It is built with Python and Tkinter.

## Requirements

- **Python 3.8+**
- Install additional dependencies with:

```bash
pip install -r requirements.txt
```

To enable receipt parsing powered by OpenAI models you must define the
`OPENAI_API_KEY` environment variable with a valid API key before running the
application.

## Modules Overview

- **controllers/** – business logic for products, purchases, recipes and more.
- **gui/** – Tkinter windows that provide the graphical interface.
- **models/** – plain Python classes that represent the domain objects.
- **views/** – command line interface utilities (legacy).
- **utils/** – helper functions used across the project.
- **data/** – JSON files where all application data is stored.
You can change this directory by setting the `CAFE_DATA_PATH` environment
variable before running the application.

## Usage

Run the application with:

```bash
python main.py
```

This command opens the main window of the system. To close the application simply click the **Salir** button or close the window normally.

### Custom data directory

By default all JSON data files are stored in the `data/` directory of the
project. You can change this location by setting the `CAFE_DATA_PATH`
environment variable to another directory before launching the program.
For example:

```bash
export CAFE_DATA_PATH=/path/to/my/data
python main.py
```

## Respaldo y restauración

Los archivos JSON con los datos de la aplicación se pueden respaldar y
restaurar manualmente.

### Crear un respaldo

Los respaldos se almacenan en `data/backups`. Para generar uno, copie el
contenido del directorio de datos actual a un subdirectorio con la fecha:

```bash
mkdir -p data/backups
cp -r data/*.json data/backups/$(date +%F)/
```

### Restaurar una versión histórica

Las versiones anteriores del contenido se guardan en `data/backups` y en
`data/history`. Para volver a un estado previo copie los archivos JSON del
subdirectorio deseado a `data/`:

```bash
cp data/backups/2024-06-15/*.json data/
# o
cp data/history/2024-01-30/*.json data/
```

⚠️ **Importante:** después de restaurar los archivos es necesario reiniciar la
aplicación para que cargue la información actualizada.


