"""Utilidades geograficas para enriquecer el ranking de alquileres."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd


CACHE_RELATIVO = Path("data") / "reference" / "montevideo_barrios_coords.csv"
ZONAS_INTERES_RELATIVO = Path("data") / "reference" / "zonas_interes.csv"
ZONAS_EVITAR_RELATIVO = Path("data") / "reference" / "zonas_evitar.csv"
ZONAS_EVITAR_GEOJSON_RELATIVO = Path("data") / "reference" / "zonas_evitar.geojson"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "rental-scraper/1.0 (local analysis)"

# Puntos simples para capturar accesibilidad general sin depender de APIs pagas.
REFERENCIAS_MONTEVIDEO = {
    "centro": (-34.9067, -56.1990),
    "tres_cruces": (-34.8933, -56.1667),
    "wtc": (-34.9020, -56.1367),
    "rambla_pocitos": (-34.9115, -56.1506),
}

COORDENADAS_BARRIOS_MONTEVIDEO = {
    "aguada": (-34.8920, -56.1916),
    "arroyo seco": (-34.8744, -56.2018),
    "atahualpa": (-34.8590, -56.1816),
    "barrio sur": (-34.9100, -56.1910),
    "bella vista": (-34.8703, -56.1989),
    "belvedere": (-34.8502, -56.2238),
    "brazo oriental": (-34.8645, -56.1783),
    "buceo": (-34.8998, -56.1354),
    "capurro bella vista": (-34.8660, -56.2105),
    "carrasco": (-34.8817, -56.0532),
    "carrasco norte": (-34.8627, -56.0614),
    "centro": (-34.9067, -56.1990),
    "cerro": (-34.8792, -56.2512),
    "ciudad vieja": (-34.9060, -56.2072),
    "colon": (-34.8065, -56.2228),
    "conciliacion": (-34.8198, -56.2290),
    "cordon": (-34.9011, -56.1793),
    "flor de maronas": (-34.8452, -56.1225),
    "goes": (-34.8826, -56.1784),
    "golf": (-34.9140, -56.1590),
    "jacinto vera": (-34.8768, -56.1710),
    "jardines del hipodromo": (-34.8374, -56.1396),
    "la blanqueada": (-34.8847, -56.1589),
    "la comercial": (-34.8877, -56.1784),
    "la teja": (-34.8600, -56.2340),
    "larranaga": (-34.8746, -56.1650),
    "malvin": (-34.8933, -56.1038),
    "malvin norte": (-34.8787, -56.1109),
    "manga": (-34.8057, -56.1247),
    "maronas": (-34.8453, -56.1308),
    "mercado modelo": (-34.8609, -56.1595),
    "montevideo": (-34.9011, -56.1645),
    "nuevo paris": (-34.8306, -56.2380),
    "palermo": (-34.9100, -56.1831),
    "parque batlle": (-34.8926, -56.1536),
    "parque rodo": (-34.9099, -56.1665),
    "paso de la arena": (-34.8107, -56.2807),
    "penarol": (-34.8269, -56.1982),
    "pocitos": (-34.9086, -56.1483),
    "pocitos nuevo": (-34.9044, -56.1369),
    "prado": (-34.8592, -56.2054),
    "prado nueva savona": (-34.8535, -56.2110),
    "puerto buceo": (-34.9070, -56.1320),
    "punta carretas": (-34.9235, -56.1593),
    "punta gorda": (-34.8900, -56.0867),
    "punta rieles": (-34.8299, -56.1008),
    "reducto": (-34.8792, -56.1886),
    "sayago": (-34.8369, -56.2114),
    "tres cruces": (-34.8933, -56.1667),
    "union": (-34.8790, -56.1363),
    "villa biarritz": (-34.9155, -56.1535),
    "villa dolores": (-34.9016, -56.1480),
    "villa munoz": (-34.8865, -56.1857),
}


def enriquecer_con_ubicacion(df: pd.DataFrame, raiz_proyecto: Path) -> pd.DataFrame:
    """Agrega coordenadas, distancias y un ajuste geografico al ranking."""
    df = df.copy()
    cache = cargar_cache_coordenadas(raiz_proyecto)
    if cache.empty:
        return _agregar_columnas_vacias(df)

    df["barrio_normalizado"] = df["barrio"].apply(normalizar_texto)
    columnas_cache = ["barrio_normalizado", "latitud", "longitud"]
    df = df.merge(cache[columnas_cache], on="barrio_normalizado", how="left")

    for nombre, (lat, lon) in REFERENCIAS_MONTEVIDEO.items():
        df[f"distancia_{nombre}_km"] = df.apply(
            lambda row: distancia_km(row.get("latitud"), row.get("longitud"), lat, lon),
            axis=1,
        )

    distancias = [f"distancia_{nombre}_km" for nombre in REFERENCIAS_MONTEVIDEO]
    df["distancia_referencia_min_km"] = df[distancias].min(axis=1)
    df["score_ubicacion"] = df["distancia_referencia_min_km"].apply(_score_ubicacion)
    df = _agregar_zonas_configurables(df, raiz_proyecto)
    return df


def _agregar_zonas_configurables(df: pd.DataFrame, raiz_proyecto: Path) -> pd.DataFrame:
    zonas_interes = _cargar_zonas(raiz_proyecto / ZONAS_INTERES_RELATIVO)
    zonas_evitar = _cargar_zonas(raiz_proyecto / ZONAS_EVITAR_RELATIVO)
    poligonos_evitar = _cargar_poligonos_geojson(raiz_proyecto / ZONAS_EVITAR_GEOJSON_RELATIVO)

    df = _agregar_score_zonas(
        df,
        zonas_interes,
        score_columna="score_zonas_interes",
        distancia_columna="distancia_zona_interes_min_km",
        nombre_columna="zona_interes_cercana",
    )
    df = _agregar_score_zonas(
        df,
        zonas_evitar,
        score_columna="penalizacion_zona_evitar",
        distancia_columna="distancia_zona_evitar_min_km",
        nombre_columna="zona_evitar_cercana",
    )
    df = _agregar_penalizacion_poligonos(df, poligonos_evitar)
    df["penalizacion_zona_evitar"] = df[["penalizacion_zona_evitar", "penalizacion_zona_evitar_geojson"]].max(axis=1)
    df["zona_evitar_cercana"] = df.apply(_nombre_zona_evitar, axis=1)
    return df


def _cargar_zonas(ruta: Path) -> list[dict[str, Any]]:
    if not ruta.exists():
        return []

    zonas = pd.read_csv(ruta)
    if zonas.empty:
        return []

    requeridas = {"nombre", "latitud", "longitud", "peso", "radio_km"}
    if not requeridas.issubset(zonas.columns):
        raise ValueError(f"{ruta} debe tener columnas: {', '.join(sorted(requeridas))}")

    zonas["latitud"] = pd.to_numeric(zonas["latitud"], errors="coerce")
    zonas["longitud"] = pd.to_numeric(zonas["longitud"], errors="coerce")
    zonas["peso"] = pd.to_numeric(zonas["peso"], errors="coerce").fillna(0)
    zonas["radio_km"] = pd.to_numeric(zonas["radio_km"], errors="coerce").fillna(1)
    zonas = zonas.dropna(subset=["latitud", "longitud"])
    return zonas.to_dict("records")


def _agregar_score_zonas(
    df: pd.DataFrame,
    zonas: list[dict[str, Any]],
    score_columna: str,
    distancia_columna: str,
    nombre_columna: str,
) -> pd.DataFrame:
    if not zonas:
        df[score_columna] = 0.0
        df[distancia_columna] = pd.NA
        df[nombre_columna] = pd.NA
        return df

    resultados = df.apply(lambda row: _score_zonas_fila(row, zonas), axis=1, result_type="expand")
    resultados.columns = [score_columna, distancia_columna, nombre_columna]
    return pd.concat([df, resultados], axis=1)


def _score_zonas_fila(row: pd.Series, zonas: list[dict[str, Any]]) -> tuple[float, float | None, str | None]:
    latitud = row.get("latitud")
    longitud = row.get("longitud")
    if pd.isna(latitud) or pd.isna(longitud):
        return 0.0, None, None

    mejor_score = 0.0
    distancia_minima: float | None = None
    zona_cercana: str | None = None
    for zona in zonas:
        distancia = distancia_km(latitud, longitud, float(zona["latitud"]), float(zona["longitud"]))
        if distancia is None:
            continue

        radio = max(float(zona.get("radio_km", 1)), 0.1)
        score = max(0.0, 1.0 - distancia / radio) * float(zona.get("peso", 0))
        if distancia_minima is None or distancia < distancia_minima:
            distancia_minima = distancia
            zona_cercana = str(zona.get("nombre", "")) or None
        mejor_score = max(mejor_score, score)

    return round(min(mejor_score, 10.0), 2), distancia_minima, zona_cercana


def _cargar_poligonos_geojson(ruta: Path) -> list[dict[str, Any]]:
    if not ruta.exists():
        return []

    with ruta.open("r", encoding="utf-8") as archivo:
        geojson = json.load(archivo)

    features = geojson.get("features", []) if isinstance(geojson, dict) else []
    poligonos: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict):
            continue
        geometry = feature.get("geometry") or {}
        properties = feature.get("properties") or {}
        nombre = str(properties.get("nombre") or properties.get("name") or "Zona a evitar")
        peso = _float_o_default(properties.get("peso"), 10.0)
        for polygon in _extraer_poligonos(geometry):
            poligonos.append({"nombre": nombre, "peso": peso, "polygon": polygon})
    return poligonos


def _extraer_poligonos(geometry: dict[str, Any]) -> list[list[list[tuple[float, float]]]]:
    tipo = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if tipo == "Polygon" and isinstance(coordinates, list):
        return [_convertir_polygon(coordinates)]
    if tipo == "MultiPolygon" and isinstance(coordinates, list):
        return [_convertir_polygon(polygon) for polygon in coordinates]
    return []


def _convertir_polygon(coordinates: list[Any]) -> list[list[tuple[float, float]]]:
    rings: list[list[tuple[float, float]]] = []
    for ring in coordinates:
        puntos: list[tuple[float, float]] = []
        for punto in ring:
            if not isinstance(punto, list | tuple) or len(punto) < 2:
                continue
            lon, lat = punto[0], punto[1]
            puntos.append((float(lat), float(lon)))
        if puntos:
            rings.append(puntos)
    return rings


def _agregar_penalizacion_poligonos(df: pd.DataFrame, poligonos: list[dict[str, Any]]) -> pd.DataFrame:
    if not poligonos:
        df["penalizacion_zona_evitar_geojson"] = 0.0
        df["zona_evitar_geojson"] = pd.NA
        return df

    resultados = df.apply(lambda row: _penalizacion_poligonos_fila(row, poligonos), axis=1, result_type="expand")
    resultados.columns = ["penalizacion_zona_evitar_geojson", "zona_evitar_geojson"]
    return pd.concat([df, resultados], axis=1)


def _penalizacion_poligonos_fila(row: pd.Series, poligonos: list[dict[str, Any]]) -> tuple[float, str | None]:
    latitud = row.get("latitud")
    longitud = row.get("longitud")
    if pd.isna(latitud) or pd.isna(longitud):
        return 0.0, None

    mejor_penalizacion = 0.0
    zona = None
    for poligono in poligonos:
        if _punto_en_polygon(float(latitud), float(longitud), poligono["polygon"]):
            penalizacion = min(_float_o_default(poligono.get("peso"), 10.0), 10.0)
            if penalizacion > mejor_penalizacion:
                mejor_penalizacion = penalizacion
                zona = str(poligono.get("nombre", "Zona a evitar"))
    return mejor_penalizacion, zona


def _punto_en_polygon(latitud: float, longitud: float, polygon: list[list[tuple[float, float]]]) -> bool:
    if not polygon:
        return False
    exterior = polygon[0]
    agujeros = polygon[1:]
    if not _punto_en_ring(latitud, longitud, exterior):
        return False
    return not any(_punto_en_ring(latitud, longitud, agujero) for agujero in agujeros)


def _punto_en_ring(latitud: float, longitud: float, ring: list[tuple[float, float]]) -> bool:
    dentro = False
    j = len(ring) - 1
    for i, (lat_i, lon_i) in enumerate(ring):
        lat_j, lon_j = ring[j]
        intersecta = (lon_i > longitud) != (lon_j > longitud) and latitud < (lat_j - lat_i) * (longitud - lon_i) / (lon_j - lon_i) + lat_i
        if intersecta:
            dentro = not dentro
        j = i
    return dentro


def _nombre_zona_evitar(row: pd.Series) -> Any:
    if row.get("penalizacion_zona_evitar_geojson", 0) >= row.get("penalizacion_zona_evitar", 0) and not pd.isna(row.get("zona_evitar_geojson")):
        return row.get("zona_evitar_geojson")
    return row.get("zona_evitar_cercana")


def _float_o_default(valor: Any, default: float) -> float:
    try:
        if pd.isna(valor):
            return default
        return float(valor)
    except (TypeError, ValueError):
        return default


def cargar_cache_coordenadas(raiz_proyecto: Path) -> pd.DataFrame:
    base = _cache_base_barrios()
    ruta_cache = raiz_proyecto / CACHE_RELATIVO
    if not ruta_cache.exists():
        return base

    cache = pd.read_csv(ruta_cache)
    if "barrio_normalizado" not in cache.columns:
        cache["barrio_normalizado"] = cache["barrio"].apply(normalizar_texto)
    cache["latitud"] = pd.to_numeric(cache["latitud"], errors="coerce")
    cache["longitud"] = pd.to_numeric(cache["longitud"], errors="coerce")
    cache = cache.dropna(subset=["barrio_normalizado", "latitud", "longitud"])
    return pd.concat([base, cache], ignore_index=True).drop_duplicates(
        subset=["barrio_normalizado"],
        keep="last",
    )


def _cache_base_barrios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"barrio_normalizado": barrio, "latitud": latitud, "longitud": longitud}
            for barrio, (latitud, longitud) in COORDENADAS_BARRIOS_MONTEVIDEO.items()
        ]
    )


def actualizar_cache_desde_csv(raiz_proyecto: Path, pausa_segundos: float = 1.1) -> Path:
    """Geocodifica barrios del CSV del scraper y guarda un cache local."""
    ruta_datos = raiz_proyecto / "data" / "processed" / "infocasas_1_dormitorio_detalle.csv"
    if not ruta_datos.exists():
        raise FileNotFoundError(f"No existe el CSV del scraper: {ruta_datos}")

    df = pd.read_csv(ruta_datos)
    barrios = sorted({str(barrio).strip() for barrio in df.get("barrio", pd.Series(dtype=str)).dropna() if str(barrio).strip()})
    ruta_cache = raiz_proyecto / CACHE_RELATIVO
    existentes = cargar_cache_coordenadas(raiz_proyecto)
    vistos = set(existentes["barrio_normalizado"]) if not existentes.empty else set()

    filas = existentes.to_dict("records") if not existentes.empty else []
    for barrio in barrios:
        barrio_normalizado = normalizar_texto(barrio)
        if barrio_normalizado in vistos:
            continue

        resultado = geocodificar_barrio(barrio)
        if resultado is not None:
            latitud, longitud, display_name = resultado
            filas.append(
                {
                    "barrio": barrio,
                    "barrio_normalizado": barrio_normalizado,
                    "latitud": latitud,
                    "longitud": longitud,
                    "fuente": "nominatim",
                    "display_name": display_name,
                }
            )
            vistos.add(barrio_normalizado)
            print(f"OK {barrio}: {latitud:.5f}, {longitud:.5f}")
        else:
            print(f"Sin resultado: {barrio}")

        time.sleep(pausa_segundos)

    ruta_cache.parent.mkdir(parents=True, exist_ok=True)
    with ruta_cache.open("w", newline="", encoding="utf-8") as archivo:
        columnas = ["barrio", "barrio_normalizado", "latitud", "longitud", "fuente", "display_name"]
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(filas)

    return ruta_cache


def geocodificar_barrio(barrio: str) -> tuple[float, float, str] | None:
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError("Instala las dependencias con `python -m pip install -r requirements.txt` para geocodificar.") from exc

    params = {
        "q": f"{barrio}, Montevideo, Uruguay",
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }
    response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    resultados = response.json()
    if not resultados:
        return None

    item = resultados[0]
    return float(item["lat"]), float(item["lon"]), str(item.get("display_name", ""))


def distancia_km(lat1: Any, lon1: Any, lat2: float, lon2: float) -> float | None:
    if pd.isna(lat1) or pd.isna(lon1):
        return None

    radio_tierra_km = 6371.0
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - float(lat1))
    delta_lambda = math.radians(lon2 - float(lon1))
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return radio_tierra_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def normalizar_texto(valor: Any) -> str:
    if pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return texto.lower().strip()


def _score_ubicacion(distancia_minima_km: Any) -> float:
    if pd.isna(distancia_minima_km):
        return 0.0
    # Hasta 10 puntos: maximo cerca de referencias, cero desde 9 km o mas.
    return round(max(0.0, 10.0 - float(distancia_minima_km) * 1.15), 2)


def _agregar_columnas_vacias(df: pd.DataFrame) -> pd.DataFrame:
    df["latitud"] = pd.NA
    df["longitud"] = pd.NA
    df["distancia_referencia_min_km"] = pd.NA
    df["score_ubicacion"] = 0.0
    df["score_zonas_interes"] = 0.0
    df["distancia_zona_interes_min_km"] = pd.NA
    df["zona_interes_cercana"] = pd.NA
    df["penalizacion_zona_evitar"] = 0.0
    df["distancia_zona_evitar_min_km"] = pd.NA
    df["zona_evitar_cercana"] = pd.NA
    df["penalizacion_zona_evitar_geojson"] = 0.0
    df["zona_evitar_geojson"] = pd.NA
    for nombre in REFERENCIAS_MONTEVIDEO:
        df[f"distancia_{nombre}_km"] = pd.NA
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Actualiza el cache local de coordenadas por barrio.")
    parser.add_argument("--pause", type=float, default=1.1, help="Pausa entre requests a Nominatim.")
    args = parser.parse_args()

    raiz_proyecto = Path(__file__).resolve().parents[1]
    ruta_cache = actualizar_cache_desde_csv(raiz_proyecto, pausa_segundos=args.pause)
    print(f"Cache de ubicaciones guardado en: {ruta_cache}")


if __name__ == "__main__":
    main()
