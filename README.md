# Cafe Management System

This project is a simple GUI-based application for managing a cafe. It is built with Python and Tkinter.

## Requirements

- **Python 3.8+**
- Before running the application or its tests, install the required dependencies:

```bash
pip install -r requirements.txt
```

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

### Gestión de compras

El sistema permite registrar compras de materias primas y también eliminarlas
si se registraron por error. Al borrar una compra se descuenta del stock la
cantidad de cada ítem asociado para mantener la consistencia de inventario.

### Estrategia de fijación de precios

El módulo `controllers/pricing_controller.py` incluye funciones para calcular
el costo variable unitario (CV), el costo fijo unitario (CF/UP) y el precio de
venta sugerido. El valor de **UP (unidades previstas)** debe ser ingresado
manualmente por el usuario para distribuir los costos fijos del período en la
fórmula `CT = CV + (CF / UP)`.

Si se desea una distribución más justa para productos con precios distintos,
se puede usar el reparto proporcional por valor de venta. En este caso se
registra un plan de ventas (unidades previstas y precio de venta unitario por
producto), se calcula el peso de cada producto sobre las ventas totales y se
asigna el costo fijo según ese peso. El cálculo resultante devuelve un costo
fijo unitario por producto que refleja su participación en los ingresos.

**Cómo fijar el precio por producto con reparto proporcional**

1. Defina el **plan de ventas del período**: unidades previstas y precio de
   venta unitario esperado por cada producto.
2. Calcule el **costo fijo unitario proporcional** para cada producto con
   `calcular_costo_fijo_unitario_proporcional`.
3. Para cada producto, sume su **CV** (receta) con el costo fijo unitario
   proporcional y aplique el margen y el IVA con
   `calcular_precio_sugerido_proporcional`.

El resultado entrega el precio sugerido por producto respetando que los
productos de mayor valor absorben más costos fijos del período.

### Menú disponible para la venta

Los productos incluyen el indicador `disponible_venta` para decidir qué ítems
forman parte del menú activo. En **Gestión de Productos** se puede marcar o
desmarcar la opción *Disponible para la venta* y la ventana de ventas solo
mostrará los productos habilitados, permitiendo construir el menú en función del
análisis de precios y stock.

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
