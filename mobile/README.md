# Móvil (Kivy / BeeWare)

Este directorio inicia la migración del sistema de escritorio (Tkinter) hacia
una app móvil en Python.

## Estado actual

- `kivy_app.py`: dashboard base para Android/Desktop que reutiliza controladores
  existentes (`productos_controller` y `tickets_controller`).
- Objetivo de esta primera fase: validar arquitectura y flujo de datos antes de
  construir formularios completos de ventas, compras y stock.

## Ejecutar prototipo Kivy

1. Instala dependencias móviles:

```bash
pip install -r requirements-mobile.txt
```

2. Ejecuta la app base:

```bash
python mobile/kivy_app.py
```

## Empaquetado Android con Buildozer (Kivy)

Referencia rápida de pasos:

```bash
pip install buildozer cython
buildozer init
# Editar buildozer.spec (title, package.name, requirements, etc.)
buildozer -v android debug
```

> Nota: para compilar APK normalmente se usa Linux y SDK/NDK de Android.

## Ruta alternativa BeeWare

Si se quiere evaluar BeeWare, se recomienda crear una rama paralela y probar:

```bash
pip install briefcase
briefcase new
briefcase create android
briefcase build android
briefcase run android
```

Mantener ambas rutas (Kivy y BeeWare) por unas iteraciones permite comparar
rendimiento, tamaño de APK y velocidad de desarrollo.
