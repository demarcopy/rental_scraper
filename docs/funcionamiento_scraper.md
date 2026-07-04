# Funcionamiento del scraper

Este documento explica como el proyecto obtiene publicaciones de alquiler, extrae informacion relevante y genera un dataset listo para analizar.

## Objetivo tecnico

El scraper automatiza el relevamiento de publicaciones de alquiler desde InfoCasas. El flujo toma un listado inicial, identifica publicaciones individuales, visita cada detalle y extrae campos estructurados para construir un CSV consolidado.

## Librerias principales

### `requests`

Se usa para realizar requests HTTP y descargar en memoria el HTML de listados y publicaciones individuales.

### `BeautifulSoup`

Se usa para parsear HTML y localizar elementos relevantes, especialmente el bloque `__NEXT_DATA__` y enlaces de publicaciones.

### `json`

Se usa para convertir el contenido de `__NEXT_DATA__` en estructuras de Python. InfoCasas, al estar construido sobre Next.js, incluye datos estructurados dentro de este script.

### `csv`

Se usa para exportar archivos intermedios y el CSV final del scraping.

### `pathlib`

Se usa para manejar rutas de archivos de forma consistente entre sistemas operativos.

## Flujo de extraccion

1. `src/config.py` define la URL inicial del listado.
2. `src/fetcher.py` descarga HTML usando `requests`.
3. `src/parser.py` detecta la paginacion disponible desde el primer listado.
4. `src/main.py` recorre todas las paginas de listado detectadas.
5. `src/parser.py` extrae y deduplica links de publicaciones.
6. El scraper visita cada publicacion encontrada.
7. El parser lee el JSON embebido en `__NEXT_DATA__`.
8. Se extraen campos desde `pageProps.data` y `technicalSheet`.
9. Se guarda un CSV consolidado en `data/processed/`.
10. Las paginas o publicaciones fallidas se registran en un CSV de errores para revision posterior.

## Extraccion de paginas y links

El primer listado contiene links de paginacion. El scraper detecta la ultima pagina disponible desde rutas como `/pagina50` y construye el rango completo de paginas a procesar.

Cada listado contiene muchos enlaces. Para quedarse con publicaciones individuales, el parser filtra URLs que tienen estructura de ficha y terminan en un identificador numerico.

Ejemplo conceptual:

```text
/alquiler-apartamento-1-dormitorio-en-cordon/193775182
```

El segmento final funciona como identificador del aviso. Luego el link relativo se convierte en URL absoluta usando el dominio de InfoCasas.

## Extraccion de detalles

En cada publicacion, el scraper busca el script:

```html
<script id="__NEXT_DATA__" type="application/json">...</script>
```

Ese bloque contiene informacion estructurada que evita depender exclusivamente de selectores visuales del HTML.

El parser obtiene datos como:

- titulo,
- precio,
- moneda,
- monto,
- barrio,
- dormitorios,
- banios,
- metros cuadrados,
- gastos comunes,
- tipo de propiedad,
- referencia,
- descripcion.

## Salida del scraper

La salida tecnica del scraping es:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Ese archivo es el input del notebook de analisis.

## Outcome del proyecto

El CSV no es el resultado final de presentacion. El outcome principal esta en:

```text
notebooks/analisis_alquileres.ipynb
```

El notebook transforma el CSV en tablas, metricas y visualizaciones interpretables.
