# Estructura del proyecto

El repositorio separa codigo, datos, notebooks y documentacion para que el flujo sea facil de ejecutar y revisar.

## Estructura

```text
Scrapper-alquileres/
|-- docs/
|-- notebooks/
|-- src/
|-- web/
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- reference/
|-- requirements.txt
|-- README.md
`-- .gitignore
```

## `src/`

Contiene el codigo del scraper.

Archivos principales:

- `config.py`: URL inicial y configuracion base.
- `fetcher.py`: descarga HTML con `requests`.
- `parser.py`: extrae links y campos desde HTML/JSON.
- `main.py`: orquesta el scraping y exporta CSVs.

## `data/raw/`

Carpeta opcional para HTML crudo. Por defecto el scraper procesa HTML en memoria y no escribe archivos raw.

Solo se usa cuando se ejecuta con `CACHE_RAW_HTML=1`, principalmente para depurar parsing.

## `data/processed/`

Guarda salidas tecnicas del scraping.

Archivos principales:

- `infocasas_1_dormitorio_links.csv`: links detectados en todas las paginas del listado.
- `infocasas_1_dormitorio_detalle.csv`: dataset consolidado de publicaciones.
- `infocasas_1_dormitorio_errores.csv`: paginas o detalles que no pudieron descargarse.

La web y el ranking leen principalmente `infocasas_1_dormitorio_detalle.csv`.

## `data/reference/`

Guarda configuracion geografica editable por el usuario.

Archivos principales:

- `zonas_interes.csv`: puntos que suman al score geografico.
- `zonas_evitar.csv`: puntos con radio que penalizan el score geografico.
- `zonas_evitar.geojson`: poligonos que penalizan el score geografico.

## `web/`

Contiene la SPA estatica para explorar el ranking local desde `src/web_server.py`.

## `notebooks/`

Contiene el notebook principal de analisis:

```text
notebooks/analisis_alquileres.ipynb
```

Este notebook es el outcome del proyecto. Ahi se presentan tablas, transformaciones, metricas y graficos.

## `docs/`

Contiene documentacion tecnica del proyecto:

- funcionamiento del scraper,
- flujo de scraping,
- campos extraidos,
- analisis en notebook,
- estructura del repositorio.

## Archivos ignorados

El repositorio ignora archivos generados o locales:

- `.venv/`,
- `.tmp/`,
- `__pycache__/`,
- checkpoints de Jupyter,
- HTML crudo,
- cache local de Matplotlib,
- salidas derivadas de `data/processed/analysis/`,
- graficos generados opcionalmente.

Esto mantiene el repositorio enfocado en codigo, documentacion y resultados relevantes.
