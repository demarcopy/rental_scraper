# Estructura del proyecto

Para que el proyecto sea fácil de entender y mantener, conviene organizarlo por carpetas.

## Estructura sugerida

```text
scraper-infocasas/
├── docs/
├── notebooks/
├── src/
├── data/
│   ├── raw/
│   └── processed/
└── README.md
```

## Qué va en cada carpeta

### `src/`

Aquí iría el código principal del proyecto.

Por ejemplo:

- Funciones para descargar HTML.
- Funciones para parsear páginas.
- Funciones para limpiar datos.
- Funciones para exportar resultados.

La idea es que el código reusable viva aquí y no quede mezclado con pruebas sueltas.

### `data/raw/`

Aquí se guardan los datos sin limpiar.

Por ejemplo:

- HTML descargado.
- Listados originales.
- Archivos intermedios.

Sirve como respaldo y como punto de partida para volver a procesar datos.

### `data/processed/`

Aquí se guardan los datos ya limpios y listos para análisis.

Por ejemplo:

- CSV final.
- Tablas normalizadas.
- Archivos con columnas ordenadas y valores convertidos.

### `notebooks/`

Aquí van los notebooks de experimentación.

Se usan para:

- Probar ideas.
- Explorar el HTML.
- Revisar resultados.
- Documentar pasos de forma interactiva.

El notebook de referencia del proyecto puede vivir aquí si después se decide ordenar el repositorio.

### `docs/`

Aquí va la documentación del proyecto.

Sirve para dejar claro:

- Qué hace el proyecto.
- Cómo funciona el flujo.
- Qué campos se van a extraer.
- Cuáles son los próximos pasos.

## Beneficio de esta estructura

Separar código, datos y documentación ayuda a:

- Entender mejor el proyecto.
- Evitar desorden.
- Reutilizar el trabajo.
- Hacer más fácil el mantenimiento.
