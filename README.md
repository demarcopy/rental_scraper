# Scraper de alquileres

Proyecto base para extraer y analizar publicaciones de alquiler de InfoCasas.

## Estado actual

- Descarga y guarda el HTML crudo del listado.
- Extrae los links de las publicaciones del listado.
- Descarga el detalle de cada publicacion.
- Extrae campos principales de cada alquiler.
- Genera un CSV listo para analisis.

## Como correr el scraping

```bash
python src/main.py
```

## Como correr el analisis

En script:

```bash
python src/analyze.py
```

En notebook:

```text
notebooks/analisis_alquileres.ipynb
```

## Salidas generadas

- `data/raw/infocasas_1_dormitorio.html`
- `data/processed/infocasas_1_dormitorio_links.csv`
- `data/processed/infocasas_1_dormitorio_detalle.csv`
- `data/processed/analysis/alquileres_limpios.csv`
- `data/processed/analysis/*.csv`
- `data/processed/analysis/plots/*.png` si `matplotlib` esta instalado

## Analisis

El analisis considera todos los tipos de propiedad disponibles. Para comparar segmentos se usa la columna `tipo_propiedad`.

