# Guia de estudio: como funciona este scraper

Este proyecto fue pensado para aprender web scraping paso a paso con un caso real: publicaciones de alquiler en InfoCasas.

La idea no es solo "hacer que funcione", sino entender que hace cada parte del flujo y por que existe.

## Objetivo de estudio

El objetivo principal es aprender a:

- Descargar el HTML de una pagina web.
- Identificar donde estan las publicaciones dentro de ese HTML.
- Extraer los links de cada propiedad.
- Preparar el camino para entrar al detalle de cada anuncio.
- Guardar la informacion de forma ordenada para analizarla despues.

En otras palabras: primero aprender a leer la estructura de una pagina, despues a extraer datos, y por ultimo a convertir esos datos en algo util para analisis.

## Que es web scraping

Web scraping es el proceso de obtener informacion de una pagina web de forma automatica.

En vez de copiar y pegar datos manualmente, un programa:

1. Pide la pagina al servidor.
2. Recibe el HTML.
3. Busca dentro de ese HTML los elementos que interesan.
4. Extrae textos, enlaces o atributos.
5. Guarda el resultado en un formato util, como CSV.

El scraping trabaja sobre el codigo de la pagina, no sobre la pantalla que ves en el navegador.

## Librerias que usa este proyecto

### `requests`

Se usa para hacer la request HTTP y descargar el HTML.

En este proyecto, `requests.get(...)` es el paso que trae el contenido de la pagina desde internet.

### `BeautifulSoup`

Se usa para parsear el HTML.

Parsear significa convertir el texto crudo del HTML en una estructura que sea mas facil de recorrer y consultar.

Con `BeautifulSoup` se pueden:

- Buscar etiquetas como `<a>`, `<div>`, `<h1>`.
- Filtrar por atributos como `href`.
- Extraer texto.
- Recorrer el arbol del HTML.

### `csv`

Se usa para guardar los resultados en un archivo CSV simple.

En este caso, se usa para exportar la lista de links extraidos.

### `pathlib`

Se usa para trabajar con rutas de archivos de forma ordenada.

Hace mas claro donde se guarda el HTML crudo y donde se guarda la salida procesada.

## Como leer el codigo del proyecto

Si queres seguir el flujo sin perderte, conviene leer los archivos en este orden:

1. `src/config.py`
2. `src/fetcher.py`
3. `src/parser.py`
4. `src/main.py`

Cada uno cumple una funcion distinta:

- `config.py`: define la URL base y configuraciones generales.
- `fetcher.py`: descarga el HTML.
- `parser.py`: busca enlaces dentro del HTML.
- `main.py`: conecta todo y guarda los resultados.

## Como funciona el flujo actual

El proyecto hoy sigue este recorrido:

1. Se define una URL base en `src/config.py`.
2. `src/fetcher.py` intenta descargar el HTML de esa pagina.
3. Si el HTML ya existe en disco, se reutiliza el archivo local.
4. `src/parser.py` toma ese HTML y lo analiza con `BeautifulSoup`.
5. Se buscan todas las etiquetas `<a>` con `href`.
6. Se filtran los enlaces que parecen ser publicaciones individuales.
7. Se convierten los links relativos en links completos.
8. Se eliminan duplicados.
9. El resultado se guarda en un CSV dentro de `data/processed/`.

## Como extrae la informacion

La extraccion se basa en una idea simple: encontrar patrones dentro del HTML.

En el listado de InfoCasas aparecen muchas etiquetas `<a>`, pero no todas sirven.
Algunas llevan a secciones generales, otras al perfil de una inmobiliaria y otras a una publicacion concreta.

Para detectar una publicacion individual, el parser hace esto:

- Lee cada enlace `href`.
- Descarta los que no empiezan con `/`.
- Revisa si la ultima parte de la ruta es numerica.
- Si termina en un numero, se considera una publicacion.

Ejemplo conceptual:

```text
/alquiler-apartamento-1-dormitorio-amueblado-a-estrenar-y-con-garaje-punta-carretas-oda/193837553
```

La parte final `193837553` funciona como identificador de la propiedad.

Luego ese enlace relativo se convierte en una URL completa usando la base del sitio:

```text
https://www.infocasas.com.uy + /alquiler-apartamento-.../193837553
```

## Guia mental del proceso

Una buena forma de pensar el scraping es esta:

1. Pido la pagina.
2. Leo el HTML.
3. Busco patrones.
4. Filtrado lo que me interesa.
5. Guardo el resultado.

Esa secuencia se repite muchas veces, incluso cuando mas adelante extraigamos campos del detalle de cada propiedad.

## Que no hace todavia

Este proyecto aun no extrae los campos completos del detalle de cada propiedad.

Todavia faltan cosas como:

- titulo.
- precio.
- barrio.
- dormitorios.
- banios.
- metros cuadrados.
- gastos comunes.

Por eso el paso actual es importante: primero conseguir los links correctos, despues entrar a cada ficha individual.

## Ejemplo de salida

Hasta ahora el script genera un CSV con una sola columna:

```text
url
https://www.infocasas.com.uy/alquiler-de-apartamento-en-cordon-sur-10283-1-dormitorio-gran-terraza/193863958
https://www.infocasas.com.uy/alquiler-de-apartamento-de-1-dormitorio-en-cordon-sur/193775182
```

Eso no es el dataset final, pero si es la base para seguir avanzando.

## Idea clave

El scraping no consiste en "adivinar" datos, sino en reconocer estructuras repetidas en el HTML.

Cuando entiendes como esta organizada una pagina, extraer informacion se vuelve un problema de busqueda y filtrado.

Si se quiere avanzar bien, la secuencia correcta es:

1. Entender la pagina.
2. Encontrar el patron.
3. Extraer un campo.
4. Probarlo con una pagina.
5. Repetir con mas campos.
