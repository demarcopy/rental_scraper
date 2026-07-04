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

- Descarga y guarda el HTML crudo del listado.
- Extrae los links de las publicaciones del listado.
- Descarga el detalle de cada publicacion.
- Extrae campos principales de cada alquiler.
- Genera un CSV listo para analisis.

## Como correr el scraping

```bash
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

El notebook carga el CSV generado por el scraping, limpia los datos en memoria y muestra las tablas/graficos dentro del propio notebook. No se usan archivos CSV ni imagenes derivados como outcome del analisis.

## Salidas generadas

- `data/raw/infocasas_1_dormitorio.html`
- `data/processed/infocasas_1_dormitorio_links.csv`
- `data/processed/infocasas_1_dormitorio_detalle.csv`

## Analisis

El analisis considera todos los tipos de propiedad disponibles. Para comparar segmentos se usa la columna `tipo_propiedad`.
