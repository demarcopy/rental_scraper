"""Punto de entrada del scraper de InfoCasas."""

from __future__ import annotations

import csv
import argparse
from datetime import date
from pathlib import Path

from config import BASE_URL, CACHE_RAW_HTML, REQUEST_DELAY_SECONDS
from fetcher import obtener_html
from parser import (
    extraer_datos_publicacion,
    extraer_links_paginas,
    extraer_links_publicaciones,
    leer_html,
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
        "fecha_scraping",
        "mes",
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


def guardar_errores(ruta_archivo: Path, errores: list[dict[str, str]]) -> None:
    """Guarda URLs que no pudieron descargarse para revision posterior."""
    ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

    with ruta_archivo.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=["tipo", "url", "motivo"])
        writer.writeheader()
        writer.writerows(errores)


def _asegurar_html_listado(url: str, ruta_html: Path) -> str | None:
    """Obtiene HTML de listado en memoria; cachea en disco solo si esta habilitado."""
    if CACHE_RAW_HTML and ruta_html.exists():
        print(f"HTML local encontrado en: {ruta_html}")
        return leer_html(ruta_html)

    html = obtener_html(url)
    if html is None:
        return None

    if CACHE_RAW_HTML:
        guardar_texto(ruta_html, html)
        print(f"HTML guardado en: {ruta_html}")

    return html


def _ruta_html_listado(raiz_proyecto: Path, numero_pagina: int, output_prefix: str) -> Path:
    """Devuelve la ruta local usada solo cuando CACHE_RAW_HTML esta activo."""
    if numero_pagina == 1:
        return raiz_proyecto / "data" / "raw" / f"{output_prefix}.html"
    return (
        raiz_proyecto
        / "data"
        / "raw"
        / "listados"
        / f"{output_prefix}_pagina_{numero_pagina:03d}.html"
    )


def _extraer_numero_pagina_desde_url(url: str) -> int:
    """Obtiene el numero de pagina desde una URL de listado de InfoCasas."""
    import re

    match = re.search(r"/pagina(\d+)(?:$|[/?#])", url)
    return int(match.group(1)) if match else 1


def _descubrir_paginas_listado(raiz_proyecto: Path, base_url: str, output_prefix: str) -> list[str]:
    """Descubre todas las paginas disponibles desde el primer listado."""
    ruta_html = _ruta_html_listado(raiz_proyecto, 1, output_prefix)
    html = _asegurar_html_listado(base_url, ruta_html)
    if html is None:
        raise RuntimeError(f"No se pudo descargar el primer listado: {base_url}")

    paginas = [base_url, *extraer_links_paginas(html, base_url=base_url)]

    # Deduplicamos preservando orden: pagina 1 primero, luego paginas detectadas.
    vistas: set[str] = set()
    salida: list[str] = []
    for pagina in paginas:
        if pagina in vistas:
            continue
        vistas.add(pagina)
        salida.append(pagina)

    return salida


def _extraer_links_todas_las_paginas(raiz_proyecto: Path, base_url: str, output_prefix: str) -> tuple[list[str], list[dict[str, str]]]:
    """Recorre todos los listados disponibles y consolida links de publicaciones."""
    paginas = _descubrir_paginas_listado(raiz_proyecto, base_url, output_prefix)
    print(f"Paginas de listado detectadas: {len(paginas)}")

    links: list[str] = []
    vistos: set[str] = set()
    errores: list[dict[str, str]] = []

    for index, url_pagina in enumerate(paginas, start=1):
        numero_pagina = _extraer_numero_pagina_desde_url(url_pagina)
        ruta_html = _ruta_html_listado(raiz_proyecto, numero_pagina, output_prefix)
        print(f"[{index}/{len(paginas)}] Procesando listado: {url_pagina}")
        html = _asegurar_html_listado(url_pagina, ruta_html)
        if html is None:
            print("  No se pudo descargar este listado; se continua con la siguiente pagina.")
            errores.append({"tipo": "listado", "url": url_pagina, "motivo": "descarga fallida"})
            if index < len(paginas):
                import time

                time.sleep(REQUEST_DELAY_SECONDS)
            continue

        links_pagina = extraer_links_publicaciones(html, base_url=url_pagina)
        nuevos = 0
        for link in links_pagina:
            if link in vistos:
                continue
            vistos.add(link)
            links.append(link)
            nuevos += 1

        print(f"  Links nuevos: {nuevos}")

        if index < len(paginas):
            import time

            time.sleep(REQUEST_DELAY_SECONDS)

    return links, errores


def _asegurar_links(raiz_proyecto: Path, ruta_links: Path, base_url: str, output_prefix: str) -> tuple[list[str], list[dict[str, str]]]:
    """Extrae links recorriendo todas las paginas de listado detectadas."""
    links, errores = _extraer_links_todas_las_paginas(raiz_proyecto, base_url, output_prefix)
    guardar_links(ruta_links, links)
    print(f"Links guardados en: {ruta_links}")
    return links, errores


def _descargar_detalle(url: str) -> str | None:
    """Descarga el HTML de una publicación individual."""
    html = obtener_html(url)
    return html


def _parsear_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrapea publicaciones de alquiler desde InfoCasas.")
    parser.add_argument("--base-url", default=BASE_URL, help="URL del listado inicial a recorrer.")
    parser.add_argument(
        "--output-prefix",
        default="infocasas_1_dormitorio",
        help="Prefijo para CSVs generados en data/processed y HTML crudo opcional.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parsear_args()
    raiz_proyecto = Path(__file__).resolve().parents[1]
    ruta_links = raiz_proyecto / "data" / "processed" / f"{args.output_prefix}_links.csv"
    ruta_salida = raiz_proyecto / "data" / "processed" / f"{args.output_prefix}_detalle.csv"
    ruta_errores = raiz_proyecto / "data" / "processed" / f"{args.output_prefix}_errores.csv"

    links, errores = _asegurar_links(raiz_proyecto, ruta_links, args.base_url, args.output_prefix)
    print(f"Publicaciones encontradas: {len(links)}")

    filas: list[dict[str, object]] = []
    fecha_scraping = date.today().isoformat()
    mes_scraping = fecha_scraping[:7]
    for index, url in enumerate(links, start=1):
        print(f"[{index}/{len(links)}] Descargando detalle: {url}")
        html = _descargar_detalle(url)
        if html is None:
            print("  No se pudo descargar esta publicacion.")
            errores.append({"tipo": "detalle", "url": url, "motivo": "descarga fallida"})
            continue

        fila = extraer_datos_publicacion(html, url)
        fila["fecha_scraping"] = fecha_scraping
        fila["mes"] = mes_scraping
        filas.append(fila)
        print(f"  Titulo: {fila.get('titulo') or 'sin titulo'}")

        if index < len(links):
            # Pausa simple para no hacer requests consecutivas demasiado rapido.
            import time

            time.sleep(REQUEST_DELAY_SECONDS)

    guardar_resultados(ruta_salida, filas)
    guardar_errores(ruta_errores, errores)
    print(f"Resultados guardados en: {ruta_salida}")
    print(f"Errores guardados en: {ruta_errores}")
    print(f"Publicaciones procesadas: {len(filas)}")
    print(f"Errores registrados: {len(errores)}")


if __name__ == "__main__":
    main()
