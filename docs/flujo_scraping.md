# Flujo de scraping

Este documento describe el flujo operativo del scraper desde la URL inicial hasta el CSV consolidado de publicaciones.

## 1. URL objetivo

La URL inicial vive en `src/config.py`:

```python
BASE_URL = "https://www.infocasas.com.uy/alquiler/inmuebles/1-dormitorio"
```

Esa URL define el universo inicial de publicaciones. El proyecto puede ampliarse incorporando nuevas paginas, barrios, filtros o tipos de busqueda.

## 2. Descarga del HTML del listado

`src/fetcher.py` usa `requests` para obtener el HTML del listado.

Funcion principal:

```python
obtener_html(url)
```

El HTML crudo del listado se guarda en:

```text
data/raw/infocasas_1_dormitorio.html
```

Guardar HTML local permite depurar el parser y repetir pruebas sin descargar la pagina cada vez.

## 3. Extraccion de links

`src/parser.py` revisa las etiquetas `<a>` del listado y filtra enlaces que corresponden a publicaciones individuales.

La lista de links se guarda en:

```text
data/processed/infocasas_1_dormitorio_links.csv
```

Este archivo es una salida intermedia util para inspeccionar que publicaciones fueron detectadas.

## 4. Visita a cada publicacion

`src/main.py` recorre los links detectados y descarga el HTML de cada ficha individual.

Cada detalle contiene mas informacion que el listado, por eso el dataset final se construye desde las paginas individuales.

## 5. Lectura de `__NEXT_DATA__`

InfoCasas incluye datos estructurados dentro de un JSON embebido en el HTML:

```html
<script id="__NEXT_DATA__" type="application/json">...</script>
```

El scraper parsea ese JSON y toma informacion desde estructuras como `pageProps.data` y `technicalSheet`.

Esta estrategia es mas estable que depender solo de clases CSS visuales.

## 6. Normalizacion de campos

Durante la extraccion se consolidan campos utiles para analisis:

- identificacion de la publicacion,
- ubicacion,
- precio,
- moneda,
- caracteristicas fisicas,
- tipo de propiedad,
- gastos comunes,
- descripcion.

## 7. CSV consolidado

La salida final del scraping se guarda en:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Este archivo es el input del notebook.

## 8. Analisis en notebook

El analisis se realiza en:

```text
notebooks/analisis_alquileres.ipynb
```

El notebook es el outcome principal: ahi se muestran tablas, metricas y graficos.

## 9. Exportacion opcional

Si se necesita compartir una tabla puntual, el notebook puede exportarla a CSV con `to_csv`.

Ejemplo:

```python
precio_tipo.to_csv("data/processed/analysis/precio_por_tipo_propiedad.csv", index=False)
```

Esa exportacion es opcional. La fuente principal de lectura y presentacion del analisis sigue siendo el notebook.
