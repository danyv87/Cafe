# Cafe Management System

This project is a simple GUI-based application for managing a cafe. It is built with Python and Tkinter.

## Requirements

- **Python 3.8+**
- Before running the application or its tests, install the required dependencies:

```bash
pip install -r requirements.txt
```

The application integrates with Google’s Gemini models through the
`google-genai` library. Version **1.0.0** or newer is required because the
receipt parser relies on the `Client.models.generate_content` API introduced
in that release. Any feature that relies on this service requires an API key.
Define the `GEMINI_API_KEY` environment variable or provide an encrypted
configuration file before running the application. If the key is missing the
program will raise an informative error.

## Modules Overview

- **controllers/** – business logic for products, purchases, recipes and more.
- **gui/** – Tkinter windows that provide the graphical interface.
- **models/** – plain Python classes that represent the domain objects.
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

### Estado de resultados

Desde el menú **Informes y Análisis** se puede abrir la pestaña *Estado Resultado*. Ingrese una fecha de inicio y otra de fin en formato `YYYY-MM-DD` y presione **Generar** para visualizar las ventas, los costos de producción calculados a partir de las recetas, los gastos adicionales y el resultado neto del período.

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



### Eliminación de compras

Desde el menú **Informes y Análisis** puedes abrir la opción *Eliminar Compras* para
quitar una compra registrada. Al confirmar la eliminación se revertirá el stock de
cada materia prima incluida en esa compra.

⚠️ **Advertencia:** si el stock actual es menor al que se pretende revertir, la operación
fallará y la compra no será eliminada.

#### Uso por consola / API

```python
from controllers.compras_controller import eliminar_compra
eliminar_compra("ID_DE_COMPRA")
```
El método devuelve ``True`` si la compra se eliminó.
## Receipts con Gemini

La aplicación puede extraer ítems de comprobantes usando los modelos de Gemini.
El lector de facturas depende exclusivamente del módulo `utils/gemini_receipt_parser`.

- **Instalación:** agrega la dependencia `google-genai` en la versión
  **1.0.0** (o superior):

```bash
pip install google-genai==1.0.0
```

- **Credenciales:** define la variable de entorno `GEMINI_API_KEY` con tu clave o utiliza el archivo de configuración cifrado proporcionado por el equipo. Sin esta información el backend no estará disponible.

- **Limitaciones y costos:** el servicio de Gemini tiene cuotas y posibles cargos según tu cuenta de Google Cloud. Revisa la documentación oficial antes de procesar comprobantes de manera masiva.

La función `utils/receipt_parser.parse_receipt_image` detecta automáticamente imágenes (`.png`, `.jpg`, `.jpeg`) y emplea este backend cuando está instalado y configurado.


