"""Calculo del ranking de oportunidades para alquileres."""

from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from location import enriquecer_con_ubicacion
except ModuleNotFoundError:  # Permite importar como src.ranking en verificaciones/tests.
    from src.location import enriquecer_con_ubicacion


TIPO_CAMBIO_USD_UYU = 40

PESOS_RANKING = {
    "descuento_total": 60,
    "descuento_m2": 30,
    "facilidad": 3,
    "ubicacion": 1,
    "zonas_interes": 1,
    "zonas_evitar": 1,
    "penalizacion_gastos_no_informados": 8,
    "penalizacion_gastos_altos": 10,
}

MONTEVIDEO_BARRIOS = {
    "aguada",
    "arroyo seco",
    "atahualpa",
    "barrio sur",
    "bella vista",
    "belvedere",
    "brazo oriental",
    "buceo",
    "capurro bella vista",
    "carrasco",
    "carrasco norte",
    "centro",
    "cerro",
    "ciudad vieja",
    "colon",
    "conciliacion",
    "cordon",
    "flor de maronas",
    "goes",
    "golf",
    "jacinto vera",
    "jardines del hipodromo",
    "la blanqueada",
    "la comercial",
    "la teja",
    "larranaga",
    "malvin",
    "malvin norte",
    "manga",
    "maronas",
    "mercado modelo",
    "montevideo",
    "nuevo paris",
    "palermo",
    "parque batlle",
    "parque rodo",
    "paso de la arena",
    "penarol",
    "pocitos",
    "pocitos nuevo",
    "prado",
    "prado nueva savona",
    "puerto buceo",
    "punta carretas",
    "punta gorda",
    "punta rieles",
    "reducto",
    "sayago",
    "tres cruces",
    "union",
    "villa biarritz",
    "villa dolores",
    "villa munoz",
}

FACILIDADES = {
    "tiene_garaje": ("Garaje", r"\b(?:garaje|garage|cochera|estacionamiento)\b"),
    "acepta_mascotas": ("Mascotas", r"(?:acepta mascota|permite mascota|pet friendly|mascotas)"),
    "amoblado": ("Amoblado", r"\b(?:amoblado|amueblado|equipado|muebles)\b"),
    "a_estrenar": ("A estrenar", r"a estrenar|nuevo"),
    "tiene_terraza": ("Terraza", r"\b(?:terraza|balcon)\b"),
    "tiene_patio": ("Patio", r"\bpatio\b"),
    "tiene_parrillero": ("Parrillero", r"\b(?:parrillero|barbacoa|parrilla)\b"),
    "tiene_laundry": ("Laundry", r"\b(?:laundry|lavadero|lavanderia)\b"),
    "tiene_gimnasio": ("Gimnasio", r"\b(?:gimnasio|gym)\b"),
    "tiene_cowork": ("Cowork", r"\b(?:cowork|co-work|coworking|business center)\b"),
    "tiene_seguridad": ("Seguridad", r"\b(?:seguridad|porteria|vigilancia|cctv|portero)\b"),
    "tiene_aire_acondicionado": ("Aire acondicionado", r"aire acondicionado|\baa\b|split"),
    "garantia_flexible": ("Garantia flexible", r"anda|contaduria|cgn|porto|sura|mapfre|aseguradora|deposito"),
}


def cargar_ranking(raiz_proyecto: Path) -> dict[str, Any]:
    """Carga el CSV del scraper y devuelve ranking, filtros y resumen para la SPA."""
    ruta_csv = raiz_proyecto / "data" / "processed" / "infocasas_1_dormitorio_detalle.csv"
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No existe el CSV del scraper: {ruta_csv}")

    df = pd.read_csv(ruta_csv)
    if df.empty:
        return _respuesta_vacia(ruta_csv)

    df = _preparar_datos(df)
    df = enriquecer_con_ubicacion(df, raiz_proyecto)
    df = _calcular_score(df)
    df = df.sort_values("score_oportunidad", ascending=False).reset_index(drop=True)
    df["puesto"] = df.index + 1

    registros = [_fila_a_dict(row) for _, row in df.iterrows()]
    barrios = sorted({item["barrio"] for item in registros if item["barrio"]})

    return {
        "source": str(ruta_csv),
        "total": len(registros),
        "updated_at": _valor(df["fecha_scraping"].dropna().max()) if "fecha_scraping" in df.columns else None,
        "filters": {
            "barrios": barrios,
            "facilidades": [
                {"key": key, "label": label} for key, (label, _) in FACILIDADES.items()
            ],
            "precio_min": _numero_min(df["costo_mensual_total_pesos"]),
            "precio_max": _numero_max(df["costo_mensual_total_pesos"]),
        },
        "weights": PESOS_RANKING,
        "rentals": registros,
    }


def _preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for columna in ["monto", "dormitorios", "banios", "metros_cuadrados"]:
        df[columna] = pd.to_numeric(df.get(columna), errors="coerce")

    if "fecha_scraping" not in df.columns:
        df["fecha_scraping"] = pd.NA


    df["gastos_comunes_informados"] = df.get("gastos_comunes", pd.Series(index=df.index)).apply(_gasto_informado)
    df["gastos_comunes_pesos"] = df.get("gastos_comunes", pd.Series(index=df.index)).apply(_limpiar_monto_gastos)
    df["alquiler_pesos"] = df.apply(_convertir_alquiler_a_pesos, axis=1)
    df["costo_mensual_total_pesos"] = df["alquiler_pesos"] + df["gastos_comunes_pesos"]
    df["gastos_sobre_alquiler_pct"] = df["gastos_comunes_pesos"] / df["alquiler_pesos"]
    df.loc[df["metros_cuadrados"] <= 0, "metros_cuadrados"] = pd.NA
    df["precio_m2_pesos"] = df["alquiler_pesos"] / df["metros_cuadrados"]
    df["costo_total_m2_pesos"] = df["costo_mensual_total_pesos"] / df["metros_cuadrados"]

    texto = df.get("titulo", "").fillna("") + " " + df.get("descripcion", "").fillna("")
    df["texto_busqueda"] = texto.apply(_normalizar_texto)
    for columna, (_, patron) in FACILIDADES.items():
        df[columna] = df["texto_busqueda"].str.contains(patron, regex=True, na=False)
    df["cantidad_facilidades"] = df[list(FACILIDADES)].sum(axis=1)

    return df


def _calcular_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        df["moneda"].isin(["$", "U$S"])
        & (df["tipo_propiedad"].apply(_normalizar_texto) == "apartamento")
        & (df["barrio"].apply(_normalizar_texto).isin(MONTEVIDEO_BARRIOS))
        & df["alquiler_pesos"].notna()
    ].copy()

    segmento = ["barrio", "dormitorios"]
    df["cantidad_comparables"] = df.groupby(segmento)["url"].transform("count")
    costo_mediano = df.groupby(segmento)["costo_mensual_total_pesos"].median().rename("costo_mediano_segmento")
    precio_m2_mediano = df.dropna(subset=["precio_m2_pesos"]).groupby(segmento)["precio_m2_pesos"].median().rename("precio_m2_mediano_segmento")
    df = df.join(costo_mediano, on=segmento)
    df = df.join(precio_m2_mediano, on=segmento)

    df["descuento_vs_segmento_pct"] = pd.to_numeric((
        df["costo_mediano_segmento"] - df["costo_mensual_total_pesos"]
    ) / df["costo_mediano_segmento"], errors="coerce")
    df["descuento_m2_vs_segmento_pct"] = pd.to_numeric((
        df["precio_m2_mediano_segmento"] - df["precio_m2_pesos"]
    ) / df["precio_m2_mediano_segmento"], errors="coerce")
    df["gastos_sobre_alquiler_pct"] = pd.to_numeric(df["gastos_sobre_alquiler_pct"], errors="coerce")
    df["descuento_total_clip"] = df["descuento_vs_segmento_pct"].fillna(0).clip(-0.5, 0.5)
    df["descuento_m2_clip"] = df["descuento_m2_vs_segmento_pct"].fillna(0).clip(-0.5, 0.5)
    df["facilidades_clip"] = df["cantidad_facilidades"].clip(upper=8)
    df["penalizacion_gastos_no_informados"] = (~df["gastos_comunes_informados"]).astype(int)
    df["penalizacion_gastos_altos"] = (df["gastos_sobre_alquiler_pct"].fillna(0) > 0.25).astype(int)

    df["score_oportunidad"] = (
        df["descuento_total_clip"] * PESOS_RANKING["descuento_total"]
        + df["descuento_m2_clip"] * PESOS_RANKING["descuento_m2"]
        + df["facilidades_clip"] * PESOS_RANKING["facilidad"]
        + df["score_ubicacion"].fillna(0) * PESOS_RANKING["ubicacion"]
        + df["score_zonas_interes"].fillna(0) * PESOS_RANKING["zonas_interes"]
        - df["penalizacion_zona_evitar"].fillna(0) * PESOS_RANKING["zonas_evitar"]
        - df["penalizacion_gastos_no_informados"] * PESOS_RANKING["penalizacion_gastos_no_informados"]
        - df["penalizacion_gastos_altos"] * PESOS_RANKING["penalizacion_gastos_altos"]
    )

    return df[df["cantidad_comparables"] >= 5].copy()


def _fila_a_dict(row: pd.Series) -> dict[str, Any]:
    facilidades = [label for key, (label, _) in FACILIDADES.items() if bool(row.get(key, False))]
    return {
        "puesto": int(row["puesto"]),
        "score": round(float(row["score_oportunidad"]), 1),
        "score_base": round(float(row["score_oportunidad"]), 1),
        "url": _valor(row.get("url")),
        "titulo": _valor(row.get("titulo")),
        "barrio": _valor(row.get("barrio")),
        "tipo_propiedad": _valor(row.get("tipo_propiedad")),
        "moneda": _valor(row.get("moneda")),
        "monto": _valor(row.get("monto")),
        "alquiler_pesos": _valor(row.get("alquiler_pesos")),
        "gastos_comunes_pesos": _valor(row.get("gastos_comunes_pesos")),
        "costo_mensual_total_pesos": _valor(row.get("costo_mensual_total_pesos")),
        "metros_cuadrados": _valor(row.get("metros_cuadrados")),
        "precio_m2_pesos": _valor(row.get("precio_m2_pesos")),
        "costo_total_m2_pesos": _valor(row.get("costo_total_m2_pesos")),
        "latitud": _valor(row.get("latitud")),
        "longitud": _valor(row.get("longitud")),
        "distancia_referencia_min_km": _valor(row.get("distancia_referencia_min_km")),
        "score_ubicacion": _valor(row.get("score_ubicacion")),
        "score_zonas_interes": _valor(row.get("score_zonas_interes")),
        "distancia_zona_interes_min_km": _valor(row.get("distancia_zona_interes_min_km")),
        "zona_interes_cercana": _valor(row.get("zona_interes_cercana")),
        "penalizacion_zona_evitar": _valor(row.get("penalizacion_zona_evitar")),
        "distancia_zona_evitar_min_km": _valor(row.get("distancia_zona_evitar_min_km")),
        "zona_evitar_cercana": _valor(row.get("zona_evitar_cercana")),
        "dormitorios": _valor(row.get("dormitorios")),
        "banios": _valor(row.get("banios")),
        "cantidad_comparables": int(row.get("cantidad_comparables", 0)),
        "descuento_vs_segmento_pct": _valor(row.get("descuento_vs_segmento_pct")),
        "descuento_m2_vs_segmento_pct": _valor(row.get("descuento_m2_vs_segmento_pct")),
        "cantidad_facilidades": int(row.get("cantidad_facilidades", 0)),
        "facilidades": facilidades,
        "facilidades_keys": [key for key in FACILIDADES if bool(row.get(key, False))],
        "gastos_comunes_informados": bool(row.get("gastos_comunes_informados", False)),
        "score_inputs": {
            "descuento_total": _valor(row.get("descuento_total_clip")),
            "descuento_m2": _valor(row.get("descuento_m2_clip")),
            "facilidades": _valor(row.get("facilidades_clip")),
            "ubicacion": _valor(row.get("score_ubicacion")),
            "zonas_interes": _valor(row.get("score_zonas_interes")),
            "zonas_evitar": _valor(row.get("penalizacion_zona_evitar")),
            "penalizacion_gastos_no_informados": _valor(row.get("penalizacion_gastos_no_informados")),
            "penalizacion_gastos_altos": _valor(row.get("penalizacion_gastos_altos")),
        },
    }


def _limpiar_monto_gastos(valor: Any) -> float:
    if pd.isna(valor):
        return 0.0
    texto = str(valor).strip()
    if not texto:
        return 0.0
    numero = re.sub(r"[^0-9]", "", texto)
    monto = float(numero) if numero else 0.0
    return monto * TIPO_CAMBIO_USD_UYU if "U$S" in texto.upper() else monto


def _gasto_informado(valor: Any) -> bool:
    return not pd.isna(valor) and bool(str(valor).strip())


def _convertir_alquiler_a_pesos(row: pd.Series) -> float | pd.NA:
    if row.get("moneda") == "U$S":
        return row.get("monto") * TIPO_CAMBIO_USD_UYU
    if row.get("moneda") == "$":
        return row.get("monto")
    return pd.NA


def _normalizar_texto(valor: Any) -> str:
    if pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return texto.lower()


def _valor(valor: Any) -> Any:
    if pd.isna(valor):
        return None
    if isinstance(valor, float) and (math.isinf(valor) or math.isnan(valor)):
        return None
    if hasattr(valor, "item"):
        return valor.item()
    return valor


def _numero_min(serie: pd.Series) -> int | None:
    valores = serie.dropna()
    return int(valores.min()) if not valores.empty else None


def _numero_max(serie: pd.Series) -> int | None:
    valores = serie.dropna()
    return int(valores.max()) if not valores.empty else None


def _respuesta_vacia(ruta_csv: Path) -> dict[str, Any]:
    return {
        "source": str(ruta_csv),
        "total": 0,
        "updated_at": None,
        "filters": {"barrios": [], "facilidades": [], "precio_min": None, "precio_max": None},
        "weights": PESOS_RANKING,
        "rentals": [],
    }
