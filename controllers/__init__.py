"""Controladores de la aplicación.

Este paquete reúne los diferentes controladores responsables de
manipular los modelos y persistir la información.  Para generar informes
con datos agregados se dispone del módulo :mod:`report_service` que
expone funciones como :func:`ventas_agrupadas` o
:func:`compras_agrupadas`.

Extender ``report_service``
--------------------------

Si en el futuro se necesita un nuevo tipo de reporte, por ejemplo
``devoluciones_agrupadas`` o ``pagos_agrupados``, se recomienda seguir
los siguientes pasos:

1. Crear una función en ``controllers/report_service.py`` con la firma
   ``nombre_agrupadas(periodo="mensual")``.
2. Importar dentro de esa función el controlador que provea los datos
   (por ejemplo ``cargar_devoluciones``).
3. Utilizar el helper ``_agrupar`` del ``report_service`` para realizar
   la agregación indicando el nombre de los atributos de fecha y monto.
4. Retornar un diccionario ``{periodo: monto}`` **sin** formatear.  Las
   vistas serán las encargadas de aplicar la función
   ``format_currency`` u otros formatos de presentación.

Siguiendo estas pautas se mantiene una separación clara entre la capa de
negocio y la de presentación.
"""
