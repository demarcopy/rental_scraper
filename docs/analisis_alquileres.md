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
df["costo_mensual_total"] = df["monto"] + df["gastos_comunes_monto"]
df["precio_m2"] = df["monto"] / df["metros_cuadrados"]
```

## Moneda

Si aparecen publicaciones en pesos y dolares, el analisis no compara ambos montos como si fueran equivalentes.

Primero se revisa la distribucion:

```python
df["moneda"].value_counts(dropna=False)
```

Luego las comparaciones se agrupan por `moneda` o se filtran segun el caso.

## Tablas principales

El notebook calcula tablas como:

- conteo por tipo de propiedad,
- conteo por barrio,
- resumen de precio por tipo de propiedad,
- resumen de precio por barrio,
- costo mensual total por barrio,
- precio por metro cuadrado por barrio.

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
