# Documentacion del proyecto

Este directorio describe el funcionamiento del scraper de alquileres, la estructura de los datos generados y el flujo de analisis incluido en el notebook.

El proyecto esta orientado a extraer publicaciones de alquiler desde InfoCasas, consolidar los datos principales en CSV y analizarlos de forma reproducible en Jupyter Notebook.

## Outcome principal

El resultado principal del proyecto es el notebook:

```text
notebooks/analisis_alquileres.ipynb
```

Ese notebook concentra el analisis final:

- carga el CSV generado por el scraper,
- limpia y normaliza los campos principales,
- revisa calidad de datos,
- compara alquileres por tipo de propiedad,
- compara precios por barrio,
- calcula costo mensual total,
- calcula precio por metro cuadrado cuando hay superficie valida,
- muestra tablas y graficos dentro del propio notebook.

El CSV del scraper es un insumo tecnico. El outcome analitico se presenta en el notebook.

## Exportacion opcional

El notebook puede extenderse para exportar resultados intermedios a CSV si se necesita compartir tablas o reutilizarlas en otra herramienta.

La exportacion es opcional y no reemplaza al notebook como entrega principal del analisis.

Ejemplo:

```python
precio_barrio.to_csv("data/processed/analysis/precio_por_barrio.csv", index=False)
```

## Flujo general

1. Ejecutar el scraper.
2. Generar el CSV consolidado de publicaciones.
3. Abrir el notebook de analisis.
4. Ejecutar las celdas del notebook.
5. Revisar tablas, graficos y conclusiones dentro del notebook.
6. Exportar CSVs solo si hace falta una salida adicional.

## Comandos principales

Ejecutar scraping:

```bash
python src/main.py
```

Abrir el notebook:

```bash
jupyter notebook notebooks/analisis_alquileres.ipynb
```

## Dataset generado por scraping

El scraper genera el archivo:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Cada fila representa una publicacion de alquiler y contiene campos como `url`, `titulo`, `precio`, `moneda`, `monto`, `barrio`, `dormitorios`, `banios`, `metros_cuadrados`, `gastos_comunes`, `tipo_propiedad`, `referencia` y `descripcion`.

## Documentos

- [Funcionamiento del scraper](./funcionamiento_scraper.md)
- [Flujo de scraping](./flujo_scraping.md)
- [Campos extraidos](./campos_a_extraer.md)
- [Analisis de alquileres](./analisis_alquileres.md)
- [Estructura del proyecto](./estructura_proyecto.md)

## Scraping responsable

El scraper debe ejecutarse con criterio para evitar sobrecargar el sitio objetivo.

Buenas practicas aplicadas o recomendadas:

- reutilizar HTML local cuando sea posible,
- evitar requests innecesarias,
- mantener pausas si se amplia el volumen de paginas,
- no recolectar datos personales,
- respetar los terminos de uso del sitio objetivo.
