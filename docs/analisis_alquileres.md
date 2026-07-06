# Analisis de alquileres

El analisis del proyecto se presenta en el notebook:

```text
notebooks/analisis_alquileres.ipynb
```

Ese notebook es el outcome principal del proyecto. El CSV generado por el scraper funciona como input tecnico, mientras que las tablas, metricas y graficos del notebook son la salida analitica.

## Input

El notebook consume:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Ese archivo se genera ejecutando:

```bash
python src/main.py
```

## Outcome

El notebook entrega una lectura ordenada de los alquileres obtenidos:

- volumen de publicaciones procesadas,
- tipos de propiedad detectados,
- barrios presentes en la muestra,
- distribucion de monedas,
- precios por tipo de propiedad,
- precios por barrio,
- costo mensual total incluyendo gastos comunes,
- precio por metro cuadrado cuando hay superficie valida,
- conversion de precios a pesos con tipo de cambio fijo,
- analisis de gastos comunes y su peso relativo sobre el alquiler,
- deteccion de facilidades desde titulo y descripcion,
- ranking de buenas oportunidades,
- valores faltantes y posibles problemas de calidad.

El analisis considera todos los tipos de propiedad disponibles. No esta limitado a apartamentos; `tipo_propiedad` se usa para segmentar la muestra.

## Limpieza aplicada

Dentro del notebook se realizan transformaciones en memoria:

```python
for columna in ["monto", "dormitorios", "banios", "metros_cuadrados"]:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")
```

Tambien se normalizan gastos comunes y se crean metricas derivadas:

```python
df["gastos_comunes_monto"] = df["gastos_comunes"].apply(limpiar_monto_gastos)
df["alquiler_pesos"] = df.apply(convertir_alquiler_a_pesos, axis=1)
df["gastos_comunes_pesos"] = df["gastos_comunes_monto"]
df["costo_mensual_total_pesos"] = df["alquiler_pesos"] + df["gastos_comunes_pesos"]
df["precio_m2"] = df["monto"] / df["metros_cuadrados"]
df["precio_m2_pesos"] = df["alquiler_pesos"] / df["metros_cuadrados"]
```

El tipo de cambio usado para convertir dolares a pesos queda declarado al inicio del notebook:

```python
TIPO_CAMBIO_USD_UYU = 40
```

## Moneda

Si aparecen publicaciones en pesos y dolares, el analisis no compara ambos montos como si fueran equivalentes.

Primero se revisa la distribucion:

```python
df["moneda"].value_counts(dropna=False)
```

Luego las comparaciones historicas se agrupan por `moneda`; para rankings de oportunidades se convierten a pesos con `TIPO_CAMBIO_USD_UYU = 40`.

## Tablas principales

El notebook calcula tablas como:

- conteo por tipo de propiedad,
- conteo por barrio,
- resumen de precio por tipo de propiedad,
- resumen de precio por barrio,
- costo mensual total por barrio,
- precio por metro cuadrado por barrio,
- gastos comunes por barrio,
- avisos con gastos altos,
- top de buenas oportunidades,
- top de alquileres baratos por metro cuadrado,
- top de avisos con mas facilidades.

## Ranking de oportunidades

El ranking `top_oportunidades` prioriza apartamentos en Montevideo que parecen atractivos frente a comparables del mismo `barrio` y `dormitorios`.

El dataset no trae una columna de departamento/ciudad, por lo que Montevideo se filtra mediante una lista explicita de barrios normalizados dentro del notebook.

El puntaje considera:

- descuento del costo mensual total frente a la mediana del segmento,
- descuento del precio por metro cuadrado frente a la mediana del segmento,
- cantidad de facilidades detectadas,
- penalizacion por gastos comunes no informados,
- penalizacion por gastos comunes altos respecto al alquiler.

La vista principal del ranking muestra una tabla legible con puesto, score, barrio, titulo, alquiler, gastos, total mensual, metros, total por metro cuadrado, descuentos frente a comparables, facilidades y link directo al aviso.

Este ranking es una guia para inspeccion manual, no una decision automatica.

## Facilidades

El notebook busca palabras clave en `titulo` y `descripcion` para detectar senales como garaje, mascotas, amoblado, a estrenar, terraza, patio, parrillero, laundry, gimnasio, cowork, seguridad, aire acondicionado y garantias flexibles.

Estas columnas ayudan a diferenciar ofertas baratas de ofertas realmente convenientes.

## Graficos

Los graficos se muestran dentro del notebook:

- distribucion de alquileres en pesos,
- precio mediano por barrio,
- cantidad de publicaciones por tipo de propiedad.

## Exportacion opcional a CSV

El outcome principal sigue siendo el notebook. Si hace falta generar archivos para compartir resultados puntuales, se puede agregar una celda opcional al final.

Ejemplos:

```python
from pathlib import Path

output_dir = Path("data/processed/analysis")
output_dir.mkdir(parents=True, exist_ok=True)

precio_barrio.to_csv(output_dir / "precio_por_barrio.csv", index=False)
precio_tipo.to_csv(output_dir / "precio_por_tipo_propiedad.csv", index=False)
conteo_tipo.to_csv(output_dir / "conteo_tipo_propiedad.csv", index=False)
```

Estos CSVs son derivados opcionales, no la entrega principal del proyecto.

## Limitaciones actuales

La muestra depende de la busqueda configurada en `src/config.py`.

Antes de sacar conclusiones fuertes conviene revisar:

- cantidad total de publicaciones,
- duplicados por `referencia`,
- distribucion por moneda,
- cantidad de casos por barrio,
- cantidad de casos por tipo de propiedad,
- superficies iguales a cero o faltantes.
