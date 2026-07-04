"""Punto de entrada del scraper de InfoCasas."""

from __future__ import annotations

import csv
from pathlib import Path

from config import BASE_URL, REQUEST_DELAY_SECONDS
from fetcher import obtener_html
from parser import (
    extraer_datos_publicacion,
    extraer_links_publicaciones,
    leer_html,
    leer_links_csv,
)


def guardar_texto(ruta_archivo: Path, contenido: str) -> None:
    """Guarda un texto crudo en disco."""
    ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
    ruta_archivo.write_text(contenido, encoding="utf-8")


def guardar_links(ruta_archivo: Path, links: list[str]) -> None:
    """Guarda los links extraídos en un CSV simple."""
    ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

    with ruta_archivo.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["url"])
        for link in links:
            writer.writerow([link])


def guardar_resultados(ruta_archivo: Path, filas: list[dict[str, object]]) -> None:
    """Guarda el resultado final del scraping en CSV."""
    ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

    columnas = [
        "url",
        "titulo",
        "precio",
        "moneda",
        "monto",
        "barrio",
        "dormitorios",
        "banios",
        "metros_cuadrados",
        "gastos_comunes",
        "tipo_propiedad",
        "referencia",
        "descripcion",
    ]

    with ruta_archivo.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(filas)


def _asegurar_html_listado(ruta_html: Path) -> str:
    """Obtiene el HTML del listado desde disco o desde la web."""
    if ruta_html.exists():
        print(f"HTML local encontrado en: {ruta_html}")
        return leer_html(ruta_html)

    html = obtener_html(BASE_URL)
    if html is None:
        raise RuntimeError("No se pudo descargar el HTML del listado.")

    guardar_texto(ruta_html, html)
    print(f"HTML guardado en: {ruta_html}")
    return html


def _asegurar_links(ruta_html: Path, ruta_links: Path) -> list[str]:
    """Lee links desde disco o los extrae desde el listado."""
    if ruta_links.exists():
        print(f"Links locales encontrados en: {ruta_links}")
        return leer_links_csv(ruta_links)

    html = _asegurar_html_listado(ruta_html)
    links = extraer_links_publicaciones(html)
    guardar_links(ruta_links, links)
    print(f"Links guardados en: {ruta_links}")
    return links


def _descargar_detalle(url: str) -> str | None:
    """Descarga el HTML de una publicación individual."""
    html = obtener_html(url)
    return html


def main() -> None:
    raiz_proyecto = Path(__file__).resolve().parents[1]
    ruta_html = raiz_proyecto / "data" / "raw" / "infocasas_1_dormitorio.html"
    ruta_links = raiz_proyecto / "data" / "processed" / "infocasas_1_dormitorio_links.csv"
    ruta_salida = raiz_proyecto / "data" / "processed" / "infocasas_1_dormitorio_detalle.csv"

    links = _asegurar_links(ruta_html, ruta_links)
    print(f"Publicaciones encontradas: {len(links)}")

    filas: list[dict[str, object]] = []
    for index, url in enumerate(links, start=1):
        print(f"[{index}/{len(links)}] Descargando detalle: {url}")
        html = _descargar_detalle(url)
        if html is None:
            print("  No se pudo descargar esta publicacion.")
            continue

        fila = extraer_datos_publicacion(html, url)
        filas.append(fila)
        print(f"  Titulo: {fila.get('titulo') or 'sin titulo'}")

        if index < len(links):
            # Pausa simple para no hacer requests consecutivas demasiado rapido.
            import time

            time.sleep(REQUEST_DELAY_SECONDS)

    guardar_resultados(ruta_salida, filas)
    print(f"Resultados guardados en: {ruta_salida}")
    print(f"Publicaciones procesadas: {len(filas)}")


if __name__ == "__main__":
    main()
