# Flujo de scraping

Este documento explica el flujo actual del scraper y como se conecta con el analisis posterior.

## 1. Definir la pagina objetivo

La pagina objetivo actual es un listado de alquileres de InfoCasas para inmuebles de 1 dormitorio.

La URL vive en `src/config.py`:

```python
BASE_URL = "https://www.infocasas.com.uy/alquiler/inmuebles/1-dormitorio"
```

Esta URL define el universo inicial de publicaciones. Mas adelante se puede ampliar con mas paginas, barrios o filtros.

## 2. Descargar el HTML del listado

El scraper usa `requests` para pedir el HTML de la pagina.

La funcion principal para eso esta en `src/fetcher.py`:

```python
obtener_html(url)
```

El HTML del listado se guarda en:

```text
data/raw/infocasas_1_dormitorio.html
```

Guardar el HTML crudo permite volver a parsear el listado sin repetir la request.

## 3. Extraer links de publicaciones

El parser busca etiquetas `<a>` dentro del HTML del listado.

No todos los links sirven. Por eso se filtran los enlaces que parecen publicaciones individuales, principalmente porque terminan con un identificador numerico.

El resultado se guarda en:

```text
data/processed/infocasas_1_dormitorio_links.csv
```

## 4. Entrar a cada publicacion

Con la lista de links, el scraper visita cada publicacion individual.

En cada request se obtiene el HTML del detalle. Ese detalle contiene informacion mas completa que el listado.

## 5. Leer datos estructurados desde `__NEXT_DATA__`

InfoCasas expone parte importante de la informacion dentro de un bloque JSON embebido en el HTML:

```html
<script id="__NEXT_DATA__" type="application/json">...</script>
```

El scraper parsea ese JSON y toma los datos desde `pageProps.data` y `technicalSheet`.

Esto permite extraer campos como:

- titulo,
- precio,
- moneda,
- barrio,
- dormitorios,
- banios,
- metros cuadrados,
- gastos comunes,
- tipo de propiedad,
- referencia,
- descripcion.

## 6. Exportar CSV de detalle

El resultado final del scraping se guarda en:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Este archivo es la base para el analisis de alquileres.

## 7. Limpiar datos para analisis

Antes de analizar conviene:

- convertir columnas numericas,
- revisar valores faltantes,
- normalizar gastos comunes,
- separar o convertir monedas,
- revisar superficies iguales a cero,
- eliminar duplicados usando `referencia` si se amplia la muestra.

## 8. Analizar con pandas

Con el CSV listo se pueden hacer analisis como:

- precio por tipo de propiedad,
- precio por barrio,
- costo mensual total,
- precio por metro cuadrado,
- distribucion de dormitorios y banios,
- deteccion de valores atipicos.

El analisis debe considerar todos los tipos de propiedad disponibles, usando `tipo_propiedad` para segmentar cuando sea necesario.
