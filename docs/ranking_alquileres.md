# Ranking de alquileres

Este documento explica como se calcula el ranking que muestra la web local del proyecto.

## Objetivo

El ranking prioriza publicaciones que parecen buenas oportunidades para inspeccion manual. No busca tomar una decision automatica, sino ordenar avisos usando precio relativo, metros cuadrados, gastos comunes, facilidades y ubicacion.

## Fuente de datos

La web lee:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Ese CSV es generado por el scraper y contiene titulo, URL, precio, moneda, barrio, dormitorios, banios, metros cuadrados, gastos comunes, tipo de propiedad y descripcion.

Tambien puede incluir `fecha_scraping` y `mes`. El ranking conserva esos campos para que futuras vistas puedan filtrar o comparar publicaciones por corrida mensual.

## Limpieza inicial

Antes de rankear se calculan columnas derivadas:

- `alquiler_pesos`: convierte alquileres en dolares con `TIPO_CAMBIO_USD_UYU = 40`.
- `gastos_comunes_pesos`: extrae el monto numerico de gastos comunes; si no hay dato usa `0` para el costo total, pero mantiene una marca de gasto no informado.
- `costo_mensual_total_pesos`: alquiler en pesos mas gastos comunes.
- `precio_m2_pesos`: alquiler en pesos dividido por metros cuadrados.
- `costo_total_m2_pesos`: costo mensual total dividido por metros cuadrados.

## Alcance del ranking

El ranking principal filtra:

- moneda `$` o `U$S`,
- tipo de propiedad `Apartamento`,
- barrios reconocidos como Montevideo,
- publicaciones con alquiler convertible a pesos,
- segmentos con al menos 5 comparables.

El segmento usado para comparar es:

```text
barrio + dormitorios
```

## Descuentos frente al segmento

Para cada segmento se calculan medianas:

- mediana de `costo_mensual_total_pesos`,
- mediana de `precio_m2_pesos`.

Luego cada aviso recibe dos descuentos relativos:

```text
descuento_total = (mediana_total_segmento - total_aviso) / mediana_total_segmento
descuento_m2 = (mediana_m2_segmento - precio_m2_aviso) / mediana_m2_segmento
```

Valores positivos indican que el aviso esta por debajo de la mediana del segmento. Para evitar outliers extremos, ambos descuentos se limitan al rango `-50%` a `+50%`.

## Facilidades

El modelo busca palabras clave en `titulo` y `descripcion` para detectar senales como:

- garaje,
- mascotas,
- amoblado,
- a estrenar,
- terraza,
- patio,
- parrillero,
- laundry,
- gimnasio,
- cowork,
- seguridad,
- aire acondicionado,
- garantia flexible.

La cantidad de facilidades suma valor, con tope de 8 facilidades para no sobreponderar textos muy largos.

## Ubicacion

El ranking agrega coordenadas por barrio desde `src/location.py`.

Si existe este archivo, sus datos pisan las coordenadas base:

```text
data/reference/montevideo_barrios_coords.csv
```

La ubicacion se mide como distancia minima a referencias urbanas simples:

- Centro,
- Tres Cruces,
- WTC,
- Rambla Pocitos.

El aporte geografico base es de hasta 10 puntos. Cuanto mas cerca esta el barrio de alguna referencia, mayor es el aporte. Si no hay coordenadas, el aporte geografico es `0`.

Ademas se leen zonas configurables desde:

```text
data/reference/zonas_interes.csv
data/reference/zonas_evitar.csv
data/reference/zonas_evitar.geojson
```

Las zonas de interes suman puntos por cercania a lugares importantes. Las zonas a evitar restan puntos por cercania a puntos definidos manualmente o por pertenencia a poligonos GeoJSON. El detalle de configuracion esta en `docs/geografia_ranking.md`.

## Formula base

La formula por defecto es:

```text
score =
  descuento_total_clip * 60
  + descuento_m2_clip * 30
  + facilidades_clip * 3
  + score_ubicacion * 1
  + score_zonas_interes * 1
  - penalizacion_zona_evitar * 1
  - penalizacion_gastos_no_informados * 8
  - penalizacion_gastos_altos * 10
```

Donde:

- `descuento_total_clip`: descuento total limitado entre `-0.5` y `0.5`.
- `descuento_m2_clip`: descuento por metro cuadrado limitado entre `-0.5` y `0.5`.
- `facilidades_clip`: cantidad de facilidades, con tope de 8.
- `score_ubicacion`: valor entre 0 y 10.
- `score_zonas_interes`: valor entre 0 y 10 segun cercania a zonas configuradas.
- `penalizacion_zona_evitar`: valor entre 0 y 10 segun cercania a zonas configuradas para evitar.
- `penalizacion_gastos_no_informados`: vale 1 si no se informaron gastos comunes, si no vale 0.
- `penalizacion_gastos_altos`: vale 1 si los gastos comunes superan 25% del alquiler, si no vale 0.

## Pesos ajustables en la web

La pagina permite cambiar los pesos de la formula sin modificar el CSV ni reiniciar el servidor.

Los controles cambian:

- peso del descuento frente al total mensual del segmento,
- peso del descuento por metro cuadrado,
- puntos por facilidad detectada,
- multiplicador del aporte geografico,
- peso de zonas de interes,
- peso de zonas a evitar,
- penalizacion por gastos comunes no informados,
- penalizacion por gastos comunes altos.

El recalculo ocurre en el navegador usando los componentes que devuelve `/api/rentals`.

## Interpretacion

Un score alto suele indicar una combinacion de:

- costo total menor al comparable del mismo barrio y dormitorios,
- buen precio por metro cuadrado,
- varias facilidades detectadas,
- ubicacion relativamente cercana a referencias urbanas,
- gastos comunes informados y razonables.

El score debe usarse como primer filtro. Conviene abrir el aviso y revisar estado, garantias, condiciones, direccion exacta y costos no publicados.
