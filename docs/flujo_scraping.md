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

Por defecto, el HTML se procesa en memoria y no se guarda en disco. Esto evita llenar `data/raw/` con muchas paginas de listado.

Para depurar parsing se puede activar cache raw de forma opcional:

```powershell
$env:CACHE_RAW_HTML = "1"
python src/main.py
```

## 3. Deteccion de paginacion

El primer listado incluye links de paginacion con rutas del tipo `/pagina2`. El scraper identifica la mayor pagina visible en el paginador e infiere el rango completo de paginas a recorrer.

Por ejemplo, si detecta `pagina50`, procesa desde la pagina 1 hasta la pagina 50.

## 4. Extraccion de links

`src/parser.py` revisa las etiquetas `<a>` de cada pagina de listado y filtra enlaces que corresponden a publicaciones individuales.

La lista consolidada de links se deduplica y se guarda en:

```text
data/processed/infocasas_1_dormitorio_links.csv
```

Este archivo es una salida intermedia util para inspeccionar que publicaciones fueron detectadas.

Si una pagina de listado falla luego de varios reintentos, se registra en `data/processed/infocasas_1_dormitorio_errores.csv` y el scraper continua con la siguiente pagina.

## 5. Visita a cada publicacion

`src/main.py` recorre los links detectados y descarga el HTML de cada ficha individual.

El scraper espera entre requests usando `REQUEST_DELAY_SECONDS` para evitar descargas consecutivas demasiado agresivas.

Cada detalle contiene mas informacion que el listado, por eso el dataset final se construye desde las paginas individuales.

Si una publicacion individual falla luego de varios reintentos, se registra en el CSV de errores y el proceso continua con el resto.

## 6. Lectura de `__NEXT_DATA__`

InfoCasas incluye datos estructurados dentro de un JSON embebido en el HTML:

```html
<script id="__NEXT_DATA__" type="application/json">...</script>
```

El scraper parsea ese JSON y toma informacion desde estructuras como `pageProps.data` y `technicalSheet`.

Esta estrategia es mas estable que depender solo de clases CSS visuales.

## 7. Normalizacion de campos

Durante la extraccion se consolidan campos utiles para analisis:

- identificacion de la publicacion,
- ubicacion,
- precio,
- moneda,
- caracteristicas fisicas,
- tipo de propiedad,
- gastos comunes,
- descripcion.

## 8. CSV consolidado

La salida final del scraping se guarda en:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Cada fila incluye `fecha_scraping` y `mes` para poder comparar o acumular corridas futuras.

Este archivo es el input del notebook.

## 9. Analisis en notebook

El analisis se realiza en:

```text
notebooks/analisis_alquileres.ipynb
```

El notebook es el outcome principal: ahi se muestran tablas, metricas y graficos.

## 10. Exportacion opcional

Si se necesita compartir una tabla puntual, el notebook puede exportarla a CSV con `to_csv`.

Ejemplo:

```python
precio_tipo.to_csv("data/processed/analysis/precio_por_tipo_propiedad.csv", index=False)
```

Esa exportacion es opcional. La fuente principal de lectura y presentacion del analisis sigue siendo el notebook.
