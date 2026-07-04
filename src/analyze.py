"""Analisis exploratorio de los alquileres scrapeados."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT_DIR / "data" / "processed" / "infocasas_1_dormitorio_detalle.csv"
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "analysis"


def limpiar_monto_gastos(valor: object) -> float:
    """Convierte gastos comunes como '$ 3.500' a numero."""
    if pd.isna(valor):
        return 0.0

    texto = str(valor).strip()
    if not texto:
        return 0.0

    numero = re.sub(r"[^0-9]", "", texto)
    return float(numero) if numero else 0.0


def cargar_dataset() -> pd.DataFrame:
    """Carga el CSV generado por el scraper."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No existe {INPUT_PATH}. Primero corre: python src/main.py"
        )

    return pd.read_csv(INPUT_PATH)


def preparar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas para que puedan analizarse con pandas."""
    df = df.copy()

    for columna in ["monto", "dormitorios", "banios", "metros_cuadrados"]:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    df["gastos_comunes_monto"] = df["gastos_comunes"].apply(limpiar_monto_gastos)
    df["costo_mensual_total"] = df["monto"] + df["gastos_comunes_monto"]

    df.loc[df["metros_cuadrados"] <= 0, "metros_cuadrados"] = pd.NA
    df["precio_m2"] = df["monto"] / df["metros_cuadrados"]

    return df


def generar_resumenes(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Genera tablas de resumen para revisar el mercado scrapeado."""
    resumenes = {
        "conteo_tipo_propiedad": df["tipo_propiedad"]
        .value_counts(dropna=False)
        .rename_axis("tipo_propiedad")
        .reset_index(name="cantidad"),
        "conteo_barrio": df["barrio"]
        .value_counts(dropna=False)
        .rename_axis("barrio")
        .reset_index(name="cantidad"),
        "precio_por_tipo_propiedad": df.groupby(["moneda", "tipo_propiedad"], dropna=False)[
            "monto"
        ]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index(),
        "precio_por_barrio": df.groupby(["moneda", "barrio"], dropna=False)["monto"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(["moneda", "median"], na_position="last"),
        "costo_total_por_barrio": df.groupby(["moneda", "barrio"], dropna=False)[
            "costo_mensual_total"
        ]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(["moneda", "median"], na_position="last"),
        "precio_m2_por_barrio": df.dropna(subset=["precio_m2"])
        .groupby(["moneda", "barrio"], dropna=False)["precio_m2"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(["moneda", "median"], na_position="last"),
        "valores_faltantes": df.isna()
        .sum()
        .rename_axis("columna")
        .reset_index(name="faltantes"),
    }

    return resumenes


def guardar_salidas(df: pd.DataFrame, resumenes: dict[str, pd.DataFrame]) -> None:
    """Guarda dataset limpio y tablas de resumen."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_DIR / "alquileres_limpios.csv", index=False, encoding="utf-8")
    for nombre, resumen in resumenes.items():
        resumen.to_csv(OUTPUT_DIR / f"{nombre}.csv", index=False, encoding="utf-8")


def generar_graficos(df: pd.DataFrame) -> None:
    """Genera graficos simples si matplotlib esta instalado."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no esta instalado; se omite la generacion de graficos.")
        return

    graficos_dir = OUTPUT_DIR / "plots"
    graficos_dir.mkdir(parents=True, exist_ok=True)

    df_pesos = df[df["moneda"] == "$"].copy()
    if df_pesos.empty:
        print("No hay registros en pesos para graficar precios.")
        return

    df_pesos["monto"].dropna().hist()
    plt.title("Distribucion de alquileres en pesos")
    plt.xlabel("Monto")
    plt.ylabel("Cantidad")
    plt.tight_layout()
    plt.savefig(graficos_dir / "distribucion_montos_pesos.png")
    plt.close()

    (
        df_pesos.groupby("barrio")["monto"]
        .median()
        .sort_values()
        .plot(kind="barh")
    )
    plt.title("Precio mediano por barrio")
    plt.xlabel("Monto")
    plt.ylabel("Barrio")
    plt.tight_layout()
    plt.savefig(graficos_dir / "precio_mediano_por_barrio.png")
    plt.close()

    df["tipo_propiedad"].value_counts().plot(kind="bar")
    plt.title("Publicaciones por tipo de propiedad")
    plt.xlabel("Tipo de propiedad")
    plt.ylabel("Cantidad")
    plt.tight_layout()
    plt.savefig(graficos_dir / "publicaciones_por_tipo_propiedad.png")
    plt.close()


def main() -> None:
    df = cargar_dataset()
    df_limpio = preparar_dataset(df)
    resumenes = generar_resumenes(df_limpio)
    guardar_salidas(df_limpio, resumenes)
    generar_graficos(df_limpio)

    print(f"Registros analizados: {len(df_limpio)}")
    print(f"Salidas guardadas en: {OUTPUT_DIR}")
    print("Resumenes generados:")
    for nombre in resumenes:
        print(f"- {nombre}.csv")


if __name__ == "__main__":
    main()
