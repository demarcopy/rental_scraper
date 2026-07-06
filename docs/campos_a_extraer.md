# Campos extraidos

El scraper consolida los campos principales de cada publicacion en:

```text
data/processed/infocasas_1_dormitorio_detalle.csv
```

Este CSV es el input del notebook de analisis.

## Campos del dataset

### `fecha_scraping`

Fecha en formato `YYYY-MM-DD` en la que se ejecuto el scraper y se genero la fila. Permite comparar corridas futuras sin perder trazabilidad temporal.

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

Version numerica de `gastos_comunes`. En el analisis se interpreta en pesos; si el texto indica `U$S`, se convierte usando el tipo de cambio configurado.

### `gastos_comunes_informados`

Booleano que diferencia gastos realmente informados de campos vacios. Es importante porque gastos faltantes no equivalen necesariamente a gastos cero.

### `alquiler_pesos`

Precio del alquiler convertido a pesos. Las publicaciones en dolares se convierten con `TIPO_CAMBIO_USD_UYU = 40`.

### `gastos_comunes_pesos`

Gastos comunes expresados en pesos.

### `costo_mensual_total`

Alias de compatibilidad para el costo mensual total en pesos.

### `costo_mensual_total_pesos`

Suma de `alquiler_pesos` y `gastos_comunes_pesos`.

### `gastos_sobre_alquiler_pct`

Relacion entre gastos comunes y alquiler. Ayuda a detectar gastos altos que encarecen una oferta aparentemente barata.

### `precio_m2`

Relacion entre `monto` y `metros_cuadrados`, calculada solo cuando la superficie es valida.

### `precio_m2_pesos`

Relacion entre `alquiler_pesos` y `metros_cuadrados`.

### `costo_total_m2_pesos`

Relacion entre `costo_mensual_total_pesos` y `metros_cuadrados`.

### Facilidades detectadas

El notebook crea columnas booleanas desde `titulo` y `descripcion`: `tiene_garaje`, `acepta_mascotas`, `amoblado`, `a_estrenar`, `tiene_terraza`, `tiene_patio`, `tiene_parrillero`, `tiene_laundry`, `tiene_gimnasio`, `tiene_cowork`, `tiene_seguridad`, `tiene_aire_acondicionado` y `garantia_flexible`.

### `score_oportunidad`

Puntaje analitico para priorizar buenas ofertas. Combina descuento frente a comparables del mismo barrio/tipo/dormitorios, precio por metro cuadrado, facilidades, gastos altos y gastos no informados.

## Consideraciones de calidad

Algunos campos pueden venir vacios o incompletos segun la publicacion.

Casos a revisar:

- gastos comunes no informados,
- metros cuadrados iguales a cero,
- monedas mezcladas,
- barrios con pocas publicaciones,
- tipos de propiedad con baja cantidad de casos.

Estas validaciones se realizan dentro del notebook.
