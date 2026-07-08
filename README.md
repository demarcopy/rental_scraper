# Scraper de alquileres

Proyecto base para extraer y analizar publicaciones de alquiler de InfoCasas.

## Requisitos

- Python 3.12 o superior.
- Git.
- Acceso a internet para instalar dependencias y ejecutar el scraping.

## Configurar el entorno

Desde la raiz del proyecto, crear el entorno virtual:

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si Windows bloquea permisos en la carpeta temporal, usar una carpeta temporal local del proyecto antes de instalar dependencias:

```powershell
New-Item -ItemType Directory -Force .tmp | Out-Null
$resolved = Resolve-Path .tmp
$env:TEMP = $resolved
$env:TMP = $resolved
$env:TMPDIR = $resolved
```

Actualizar `pip` e instalar todas las dependencias del proyecto:

```powershell
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Registrar el entorno como kernel de Jupyter:

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name rental-scraper --display-name "Python (rental-scraper)"
```

Abrir Jupyter Notebook desde el mismo entorno:

```powershell
.\.venv\Scripts\python.exe -m notebook
```

En Jupyter, abrir:

```text
notebooks/analisis_alquileres.ipynb
```

Y elegir el kernel:

```text
Python (rental-scraper)
```

### Nota para Windows

Si Python o `matplotlib` muestran errores de permisos en carpetas temporales o en `AppData`, el analisis ya configura una carpeta local para `matplotlib` dentro de:

```text
data/processed/analysis/matplotlib_config/
```

Esa carpeta esta ignorada por Git.

## Estado actual

- Descarga el HTML de los listados en memoria.
- Detecta la paginacion disponible y recorre todas las paginas del listado.
- Extrae y deduplica los links de publicaciones encontrados.
- Descarga el detalle de cada publicacion.
- Usa una pausa entre requests para reducir carga sobre el sitio objetivo.
- Extrae campos principales de cada alquiler.
- Genera un CSV listo para analisis, con fecha de scraping por fila.

## Como correr el scraping

```bash
python src/main.py
```

Por defecto no se guarda HTML crudo para evitar archivos pesados. El scraper tiene reintentos ante timeouts y guarda las URLs fallidas en `data/processed/infocasas_1_dormitorio_errores.csv`. Si necesitas depurar el parser, podes activar cache raw de forma opcional:

```powershell
$env:CACHE_RAW_HTML = "1"
python src/main.py
```

## Como correr el analisis

El resultado del analisis debe consultarse unicamente desde el notebook:

```bash
jupyter notebook notebooks/analisis_alquileres.ipynb
```

Tambien se puede abrir Jupyter y seleccionar manualmente:

```text
notebooks/analisis_alquileres.ipynb
```

El notebook carga el CSV generado por el scraping, limpia los datos en memoria y muestra las tablas/graficos dentro del propio notebook. El outcome principal del analisis es el notebook; si hace falta compartir tablas puntuales, se pueden exportar CSVs desde una celda opcional.

Para comparar publicaciones en pesos y dolares, el analisis convierte dolares a pesos con `TIPO_CAMBIO_USD_UYU = 40`. Ese valor esta definido al inicio del notebook y se puede ajustar para nuevas corridas.

## Salidas generadas

- `data/processed/infocasas_1_dormitorio_links.csv`
- `data/processed/infocasas_1_dormitorio_detalle.csv`
- `data/processed/infocasas_1_dormitorio_errores.csv`

## Analisis

El analisis considera todos los tipos de propiedad disponibles. Para comparar segmentos se usa la columna `tipo_propiedad`.

Tambien genera rankings para encontrar buenas oportunidades de alquiler usando costo mensual total, precio por metro cuadrado, gastos comunes y facilidades detectadas en titulo/descripcion. El ranking principal se enfoca en apartamentos de Montevideo y muestra el link directo a cada aviso.

## Como abrir la web del ranking

La web local usa el CSV generado por el scraper en `data/processed/infocasas_1_dormitorio_detalle.csv` y calcula el score con el mismo criterio del notebook. Si existe el cache `data/reference/montevideo_barrios_coords.csv`, tambien suma un ajuste geografico acotado por cercania a referencias urbanas de Montevideo.

```bash
python src/web_server.py
```

Luego abrir:

```text
http://127.0.0.1:8000
```

La SPA permite filtrar por barrio, precio mensual maximo y facilidades detectadas en titulo/descripcion.

La explicacion tecnica del ranking esta en:

```text
docs/ranking_alquileres.md
```

La configuracion de zonas geograficas esta en:

```text
docs/geografia_ranking.md
```

## Como actualizar ubicaciones

Para geocodificar los barrios del CSV usando Nominatim/OpenStreetMap y guardar un cache local:

```bash
python src/location.py
```

El cache se guarda en:

```text
data/reference/montevideo_barrios_coords.csv
```

El ranking no llama a APIs externas al abrir la web; solo usa ese cache si ya existe.
