# Android nativo (Kotlin + Jetpack Compose)

Este directorio documenta la migración desde la UI de escritorio (Tkinter) a
un frontend Android nativo con Kotlin + Jetpack Compose.

## Objetivo

- Eliminar la ruta Python móvil (Kivy/BeeWare).
- Construir una app Android nativa, manteniendo la lógica de negocio actual en
  Python a través de una API (recomendado) o migrándola progresivamente a Kotlin.

## Arquitectura recomendada

### Opción recomendada (incremental)

- **Frontend Android**: Kotlin + Jetpack Compose.
- **Backend**: API en Python (FastAPI) que reutiliza controladores existentes.
- **Persistencia**:
  - Servidor: PostgreSQL o JSON durante transición.
  - App Android: Room para caché offline.

### Capas Android

- `ui/` (Compose screens + components)
- `viewmodel/` (StateFlow, lógica de presentación)
- `data/remote/` (Retrofit API)
- `data/local/` (Room)
- `domain/` (casos de uso y modelos de dominio)

## Crear el proyecto Android

1. Abrir Android Studio.
2. `New Project` → `Empty Activity`.
3. Configurar:
   - Name: `CafeMobile`
   - Language: `Kotlin`
   - Minimum SDK: `24+`
4. Activar Compose (normalmente ya viene activo en plantillas recientes).

## Dependencias sugeridas (Gradle)

- Compose BOM
- Navigation Compose
- Lifecycle ViewModel Compose
- Retrofit + OkHttp + Kotlinx Serialization/Moshi
- Room
- Coroutines

## Plan de migración de pantallas

Mapeo sugerido desde Tkinter:

1. **Home** (menú principal)
2. **Productos**
3. **Ventas (tickets)**
4. **Compras y stock**
5. **Informes y análisis**

> Empezar por Ventas + Productos para liberar valor rápido.

## Contrato API mínimo para el MVP

- `GET /productos`
- `POST /productos`
- `PUT /productos/{id}`
- `GET /tickets`
- `POST /tickets`
- `GET /materias-primas`
- `POST /compras`

## Estado de este repo

- Se removió la ruta móvil en Python (`mobile/` y `requirements-mobile.txt`).
- Próximo paso técnico: crear módulo `api/` con FastAPI para exponer
  controladores actuales y conectarlo desde Android con Retrofit.
