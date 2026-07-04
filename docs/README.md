# Proyecto educativo de web scraping

Este proyecto tiene como objetivo aprender web scraping en Python usando publicaciones de alquiler como caso practico.

La idea no es solo hacer que el scraper funcione, sino entender el flujo completo: obtener datos desde la web, estructurarlos, guardarlos y analizarlos con `pandas`.

## Estado actual

El scraper ya completa el flujo base:

1. Descarga el HTML del listado de InfoCasas.
2. Extrae los links de las publicaciones.
3. Entra a cada publicacion.
4. Lee datos estructurados desde `__NEXT_DATA__`.
5. Exporta un CSV con datos de detalle.

La salida principal para analisis es:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

## Dataset actual

El CSV de detalle contiene una fila por publicacion y columnas como:

- `url`
- `titulo`
- `precio`
- `moneda`
- `monto`
- `barrio`
- `dormitorios`
- `banios`
- `metros_cuadrados`
- `gastos_comunes`
- `tipo_propiedad`
- `referencia`
- `descripcion`

El analisis no debe limitarse solo a apartamentos. El campo `tipo_propiedad` permite separar y comparar apartamentos, casas u otros tipos de inmueble cuando aparezcan en la muestra.

## Como correrlo

Desde la raiz del proyecto, primero se corre el scraping:

```bash
python src/main.py
```

Luego se corre el analisis:

```bash
python src/analyze.py
```

El analisis genera salidas en:

```text
data/processed/analysis/
```

Tambien hay un notebook listo para abrir en Jupyter:

```text
notebooks/analisis_alquileres.ipynb
```

## Documentacion disponible

- [Guia de estudio: como funciona este scraper](./guia_estudio_scraping.md)
- [Flujo de scraping](./flujo_scraping.md)
- [Campos extraidos](./campos_a_extraer.md)
- [Analisis de alquileres](./analisis_alquileres.md)

## Scraping responsable

Este proyecto debe hacerse con cuidado y criterio.

- No hacer demasiadas requests en poco tiempo.
- Usar pausas entre solicitudes cuando sea necesario.
- Respetar los terminos de uso del sitio.
- No intentar recolectar datos personales.
- No sobrecargar el servidor con consultas repetidas.

La idea es aprender el proceso tecnico, no afectar el funcionamiento normal del sitio.


