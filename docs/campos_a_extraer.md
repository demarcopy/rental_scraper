# Campos extraidos

El scraper consolida los campos principales de cada publicacion en:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Este CSV es el input del notebook de analisis.

## Campos del dataset

### `url`

Link completo de la publicacion. Sirve para identificar el aviso y volver a consultarlo.

### `titulo`

Titulo comercial de la publicacion. Resume tipo de inmueble, zona y atributos destacados.

### `precio`

Precio tal como aparece publicado, incluyendo moneda.

Ejemplos:

- `$ 30.000`
- `U$S 890`

### `moneda`

Moneda detectada en el precio.

Ejemplos:

- `$`
- `U$S`

Este campo es critico porque no se deben comparar montos de monedas distintas sin conversion previa.

### `monto`

Valor numerico del precio sin simbolo de moneda. Permite calcular media, mediana, minimo, maximo y otras metricas.

### `barrio`

Barrio o zona de la publicacion. Es uno de los campos principales para comparar precios.

### `dormitorios`

Cantidad de dormitorios informada en la ficha.

### `banios`

Cantidad de banios informada en la ficha.

### `metros_cuadrados`

Superficie principal extraida desde la publicacion. Puede requerir validacion porque algunos avisos informan varias superficies o valores incompletos.

### `gastos_comunes`

Texto original de gastos comunes, si esta disponible. En el notebook se convierte a una version numerica llamada `gastos_comunes_monto`.

### `tipo_propiedad`

Tipo de inmueble publicado.

Ejemplos:

- Apartamento.
- Casa.
- Oficina.
- Local.

Este campo permite analizar todos los alquileres disponibles y segmentar cuando hay suficiente muestra.

### `referencia`

Identificador interno del aviso. Es util para detectar duplicados si se amplia el scraping.

### `descripcion`

Texto descriptivo de la publicacion. Puede usarse para inspeccion manual, busqueda de palabras clave o features futuras.

## Campos derivados en el notebook

El notebook genera campos analiticos en memoria:

### `gastos_comunes_monto`

Version numerica de `gastos_comunes`.

### `costo_mensual_total`

Suma de `monto` y `gastos_comunes_monto`.

### `precio_m2`

Relacion entre `monto` y `metros_cuadrados`, calculada solo cuando la superficie es valida.

## Consideraciones de calidad

Algunos campos pueden venir vacios o incompletos segun la publicacion.

Casos a revisar:

- gastos comunes no informados,
- metros cuadrados iguales a cero,
- monedas mezcladas,
- barrios con pocas publicaciones,
- tipos de propiedad con baja cantidad de casos.

Estas validaciones se realizan dentro del notebook.
