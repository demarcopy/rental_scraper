# Estructura del proyecto

El repositorio separa codigo, datos, notebooks y documentacion para que el flujo sea facil de ejecutar y revisar.

## Estructura

```text
Scrapper-alquileres/
|-- docs/
|-- notebooks/
|-- src/
|-- data/
|   |-- raw/
|   `-- processed/
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
- `analyze.py`: script auxiliar de analisis. El outcome principal del proyecto se mantiene en el notebook.

## `data/raw/`

Guarda HTML crudo descargado desde el sitio objetivo.

Estos archivos sirven para depurar parsing y evitar requests repetidas durante el desarrollo.

## `data/processed/`

Guarda salidas tecnicas del scraping.

Archivos principales:

- `infocasas_1_dormitorio_links.csv`: links detectados.
- `infocasas_1_dormitorio_detalle.csv`: dataset consolidado de publicaciones.

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
- graficos generados opcionalmente.

Esto mantiene el repositorio enfocado en codigo, documentacion y resultados relevantes.
