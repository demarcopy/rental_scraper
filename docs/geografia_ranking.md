# Geografia del ranking

Este documento explica como configurar zonas de interes y zonas a evitar para que el ranking tenga en cuenta preferencias geograficas personales.

## Archivos configurables

La configuracion vive en `data/reference/`.

```text
data/reference/zonas_interes.csv
data/reference/zonas_evitar.csv
data/reference/zonas_evitar.geojson
```

`zonas_interes.csv` suma puntos por cercania. `zonas_evitar.csv` resta puntos por cercania a puntos con radio. `zonas_evitar.geojson` resta puntos si el aviso cae dentro de un poligono.

## Formato

Ambos CSV usan estas columnas:

```csv
nombre,tipo,latitud,longitud,peso,radio_km
```

En `zonas_evitar.csv` tambien se puede usar una columna opcional `motivo` para documentar por que se penaliza la zona.

Campos:

- `nombre`: nombre legible de la zona.
- `tipo`: categoria libre, por ejemplo `trabajo`, `transporte`, `estudio`, `servicios`, `evitar`.
- `latitud`: coordenada decimal.
- `longitud`: coordenada decimal.
- `peso`: intensidad de la zona, normalmente entre 1 y 10.
- `radio_km`: radio de influencia en kilometros.

## Zonas de interes

Ejemplo:

```csv
nombre,tipo,latitud,longitud,peso,radio_km
WTC,trabajo,-34.9020,-56.1367,10,3.0
Tres Cruces,transporte,-34.8933,-56.1667,9,2.5
Facultad de Ingenieria,estudio,-34.9182,-56.1661,7,2.0
```

Cada aviso recibe puntos si esta dentro del radio de alguna zona. Cuanto mas cerca este, mayor es el aporte. El aporte por zonas de interes se limita a 10 puntos antes de aplicar el peso configurable de la web.

## Zonas a evitar

No se cargan zonas a evitar por defecto. Esto deja la decision documentada y configurable.

Ejemplo de uso:

```csv
nombre,tipo,latitud,longitud,peso,radio_km,motivo
Zona personal a evitar,evitar,-34.8800,-56.1800,8,1.2,Preferencia personal
```

Si un aviso cae cerca de una zona a evitar, recibe una penalizacion. Cuanto mas cerca este, mayor es la penalizacion. La penalizacion por zona se limita a 10 puntos antes de aplicar el peso configurable de la web.

## Zonas a evitar con GeoJSON

Para zonas con forma irregular se puede editar:

```text
data/reference/zonas_evitar.geojson
```

El archivo debe ser un `FeatureCollection` con features `Polygon` o `MultiPolygon`. Cada feature puede tener estas propiedades:

- `nombre`: nombre visible de la zona.
- `peso`: penalizacion base, entre 1 y 10 recomendado.
- `motivo`: texto opcional para documentar el criterio.

Ejemplo minimo:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "nombre": "Zona personal a evitar",
        "peso": 8,
        "motivo": "Preferencia personal"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [-56.1900, -34.8900],
            [-56.1800, -34.8900],
            [-56.1800, -34.8800],
            [-56.1900, -34.8800],
            [-56.1900, -34.8900]
          ]
        ]
      }
    }
  ]
}
```

Importante: GeoJSON usa coordenadas en orden `[longitud, latitud]`.

Si una publicacion cae dentro de varios poligonos, se usa la penalizacion mas alta. Si tambien cae cerca de una zona de `zonas_evitar.csv`, se usa la mayor penalizacion entre CSV y GeoJSON.

## Como se calcula

Para cada aviso se usa la coordenada disponible:

- coordenada del barrio desde `src/location.py`,
- o coordenada cacheada en `data/reference/montevideo_barrios_coords.csv` si existe.

Luego se calcula distancia en linea recta a cada zona con la formula de Haversine.

Para una zona puntual:

```text
score_zona = max(0, 1 - distancia_km / radio_km) * peso
```

El ranking usa el mayor score de zona cercana, no la suma de todas. Esto evita que una zona con muchos puntos cargados alrededor domine todo el ranking.

## Pesos en la web

La SPA permite ajustar:

- `Zonas de interes`: multiplica `score_zonas_interes`.
- `Zonas a evitar`: multiplica `penalizacion_zona_evitar`.

Si subis `Zonas de interes`, priorizas avisos cerca de tus puntos importantes. Si subis `Zonas a evitar`, bajas mas fuerte los avisos cerca de puntos marcados como no deseados.

## Recomendaciones

- Usar coordenadas de puntos concretos, no nombres amplios de barrios.
- Empezar con radios entre 1 y 3 km.
- Documentar el motivo de cada zona a evitar.
- Revisar manualmente los avisos: la ubicacion puede ser aproximada si el scraper solo tiene barrio.
- No usar categorias sensibles o inferencias no verificadas; mantener las zonas como preferencias personales y explicitas.

## Limitaciones actuales

- Las distancias son en linea recta, no por recorrido real.
- Las coordenadas actuales suelen ser por barrio, no por direccion exacta.
- Las zonas a evitar son puntos con radio, no poligonos.
- Las zonas a evitar pueden ser puntos con radio o poligonos GeoJSON.

Mejoras futuras posibles:

- geocodificar direccion exacta por aviso,
- usar distancia caminando con OpenStreetMap/OSMnx,
- separar score de trabajo, transporte, estudio, parques y servicios.
