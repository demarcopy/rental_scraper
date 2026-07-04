# Campos extraidos

Estos son los campos que actualmente se extraen de cada publicacion de alquiler y se guardan en:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

## Lista de campos

### `url`

Link completo de la publicacion.

Sirve para identificar cada anuncio y volver a abrirlo mas adelante.

### `titulo`

Nombre o titulo de la propiedad.

Suele resumir el tipo de inmueble, la zona y alguna caracteristica comercial del aviso.

### `precio`

Valor mostrado en la publicacion con moneda incluida.

Ejemplos:

- `$ 30.000`
- `U$S 890`

### `moneda`

Moneda del precio.

Ejemplos:

- `$`
- `U$S`

Este campo es importante porque no conviene comparar montos en monedas distintas sin convertirlos antes.

### `monto`

Numero del precio sin el simbolo de moneda.

Este campo sirve para calculos numericos, como promedio, mediana, minimo y maximo.

### `barrio`

Zona o barrio donde esta ubicada la propiedad.

Es uno de los campos mas importantes para comparar valores.

### `dormitorios`

Cantidad de dormitorios.

### `banios`

Cantidad de banios.

### `metros_cuadrados`

Superficie principal extraida desde el detalle de la publicacion.

Puede necesitar revision porque algunas publicaciones informan varias superficies, por ejemplo edificados, terraza o terreno.

### `gastos_comunes`

Costo mensual de gastos comunes, si la publicacion lo informa.

No siempre aparece. Para analizarlo conviene crear una version numerica, por ejemplo `gastos_comunes_monto`.

### `tipo_propiedad`

Tipo de inmueble.

Ejemplos:

- Apartamento.
- Casa.
- Local.
- Oficina.

Este campo permite analizar todos los alquileres y no limitarse a apartamentos.

### `referencia`

Identificador interno o referencia del aviso.

Es util para eliminar duplicados cuando se amplie el scraping.

### `descripcion`

Texto descriptivo de la publicacion.

Puede servir para analisis exploratorio posterior, busqueda de palabras clave o deteccion de caracteristicas no estructuradas.

## Campos que pueden venir vacios

Es normal que algunos campos falten en varias publicaciones.

En especial pueden venir vacios:

- `gastos_comunes`
- `metros_cuadrados`
- `descripcion`

Por eso conviene tratar los datos faltantes desde el principio y no asumir que todas las publicaciones tienen la misma estructura.

## Campos clave para analisis

Para el analisis de alquileres, los campos mas importantes son:

- `tipo_propiedad`
- `barrio`
- `moneda`
- `monto`
- `gastos_comunes`
- `dormitorios`
- `banios`
- `metros_cuadrados`

El primer paso analitico no deberia filtrar por apartamentos, sino revisar la distribucion de `tipo_propiedad` y decidir si se analiza todo junto o por segmentos.
