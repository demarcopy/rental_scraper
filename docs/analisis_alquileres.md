# Analisis de alquileres

Este documento define como avanzar desde el CSV generado por el scraper hacia un analisis exploratorio de alquileres, considerando todos los tipos de propiedad disponibles.

## Archivo de entrada

La fuente principal es:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Este archivo se genera corriendo:

```bash
python src/main.py
```

El analisis reproducible se puede ejecutar con:

```bash
python src/analyze.py
```

Ese comando genera salidas en:

```text
data/processed/analysis/
```

## Objetivo del analisis

El objetivo es entender el comportamiento de los alquileres obtenidos:

- que tipos de propiedad aparecen,
- que barrios aparecen,
- cuanto cuestan los alquileres,
- cuanto pesan los gastos comunes,
- como cambia el precio por tipo de propiedad,
- como cambia el precio por barrio,
- y si existen valores atipicos o datos faltantes.

## Carga inicial

```python
import pandas as pd

ruta = "data/processed/infocasas_1_dormitorio_detalle.csv"
df = pd.read_csv(ruta)
```

## Revision inicial

Antes de limpiar, conviene mirar el tamano y la composicion del dataset:

```python
df.shape
df.head()
df.info()
df["tipo_propiedad"].value_counts(dropna=False)
df["barrio"].value_counts(dropna=False)
df.isna().sum()
```

## Limpieza minima recomendada

Convertir columnas numericas:

```python
columnas_numericas = ["monto", "dormitorios", "banios", "metros_cuadrados"]

for columna in columnas_numericas:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")
```

Normalizar gastos comunes:

```python
df["gastos_comunes_monto"] = (
    df["gastos_comunes"]
    .fillna("0")
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace("U$S", "", regex=False)
    .str.replace(".", "", regex=False)
    .str.strip()
)

df["gastos_comunes_monto"] = pd.to_numeric(
    df["gastos_comunes_monto"],
    errors="coerce",
).fillna(0)
```

Crear costo mensual total:

```python
df["costo_mensual_total"] = df["monto"] + df["gastos_comunes_monto"]
```

## Advertencia sobre moneda

Si el dataset mezcla pesos y dolares, no se deben comparar los valores de `monto` directamente.

Primero hay que revisar:

```python
df["moneda"].value_counts(dropna=False)
```

Para un primer analisis simple se puede trabajar solo con pesos:

```python
df_pesos = df[df["moneda"] == "$"].copy()
```

Mas adelante se puede agregar una conversion a pesos uruguayos para comparar todo junto.

## Preguntas iniciales

Estas preguntas sirven para orientar el primer analisis:

- Cual es el precio promedio y mediano de los alquileres?
- Que tipos de propiedad aparecen en la muestra?
- Que barrios tienen mas publicaciones?
- Que barrios tienen alquileres mas caros?
- Como cambia el precio entre distintos tipos de propiedad?
- Cuanto cambia el resultado si se suman gastos comunes?
- Hay publicaciones con `metros_cuadrados` igual a 0?
- Hay precios en dolares mezclados con pesos?

## Analisis sugeridos

### Distribucion de tipos de propiedad

```python
df["tipo_propiedad"].value_counts(dropna=False)
```

### Resumen general de precios

```python
df.groupby("moneda")["monto"].describe()
```

### Precio por tipo de propiedad

```python
df.groupby(["moneda", "tipo_propiedad"])["monto"].agg([
    "count",
    "mean",
    "median",
    "min",
    "max",
])
```

### Precio por barrio

```python
df.groupby(["moneda", "barrio"])["monto"].agg([
    "count",
    "mean",
    "median",
    "min",
    "max",
]).sort_values(["moneda", "median"])
```

### Costo total por barrio

```python
df.groupby(["moneda", "barrio"])["costo_mensual_total"].agg([
    "count",
    "mean",
    "median",
])
```

### Precio por metro cuadrado

```python
df["precio_m2"] = df["monto"] / df["metros_cuadrados"]

df[["tipo_propiedad", "barrio", "monto", "metros_cuadrados", "precio_m2"]]
```

Antes de usar `precio_m2`, conviene excluir superficies vacias o iguales a cero:

```python
df_m2 = df[df["metros_cuadrados"] > 0].copy()
df_m2["precio_m2"] = df_m2["monto"] / df_m2["metros_cuadrados"]
```

## Graficos utiles

Distribucion de precios:

```python
df_pesos["monto"].hist()
```

Precio mediano por barrio:

```python
(
    df_pesos.groupby("barrio")["monto"]
    .median()
    .sort_values()
    .plot(kind="barh")
)
```

Cantidad de publicaciones por tipo de propiedad:

```python
df["tipo_propiedad"].value_counts().plot(kind="bar")
```

## Advertencias sobre la muestra

La muestra actual viene de una busqueda especifica de 1 dormitorio y puede estar limitada por la pagina objetivo.

Antes de sacar conclusiones fuertes conviene:

- ampliar la cantidad de paginas,
- scrapear barrio por barrio,
- eliminar duplicados usando `referencia`,
- revisar moneda antes de comparar precios,
- separar analisis por `tipo_propiedad` cuando haya suficientes casos,
- y documentar cuantos registros entran en cada conclusion.

