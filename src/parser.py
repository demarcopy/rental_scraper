"""Utilidades para parsear el HTML del listado y del detalle de InfoCasas."""

from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config import BASE_URL


def leer_html(ruta_archivo: Path) -> str:
    """Lee el HTML crudo guardado en disco."""
    return ruta_archivo.read_text(encoding="utf-8")


def leer_links_csv(ruta_archivo: Path) -> list[str]:
    """Lee el CSV de links y devuelve una lista de URLs."""
    links: list[str] = []
    for i, line in enumerate(ruta_archivo.read_text(encoding="utf-8").splitlines()):
        if i == 0:
            continue
        link = line.strip()
        if link:
            links.append(link)
    return links


def extraer_links_publicaciones(html: str, base_url: str = BASE_URL) -> list[str]:
    """Extrae los links absolutos de las publicaciones del listado.

    El listado contiene varios enlaces que no son propiedades, por eso filtramos
    los href que terminan en un identificador numérico.
    """
    soup = BeautifulSoup(html, "html.parser")
    enlaces: list[str] = []
    vistos: set[str] = set()

    # Recorremos todos los enlaces del HTML y nos quedamos solo con los que
    # parecen apuntar a una publicación individual.
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()
        if not href.startswith("/"):
            continue
        if not _es_link_de_publicacion(href):
            continue

        # Convertimos la ruta relativa en una URL completa y evitamos duplicados.
        enlace_absoluto = urljoin(base_url, href)
        if enlace_absoluto in vistos:
            continue

        vistos.add(enlace_absoluto)
        enlaces.append(enlace_absoluto)

    return enlaces


def extraer_links_paginas(html: str, base_url: str = BASE_URL) -> list[str]:
    """Extrae links absolutos de todas las paginas disponibles en el listado.

    InfoCasas expone la paginacion como rutas del tipo ``/pagina2``.
    El paginador puede mostrar solo una ventana parcial y el ultimo numero;
    por eso inferimos el rango completo hasta la mayor pagina detectada.
    """
    soup = BeautifulSoup(html, "html.parser")
    numeros_paginas: set[int] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()
        numero_pagina = _extraer_numero_pagina(href)
        if numero_pagina is None:
            continue
        numeros_paginas.add(numero_pagina)

    if not numeros_paginas:
        return []

    ultima_pagina = max(numeros_paginas)
    base_listado = base_url.rstrip("/")
    return [f"{base_listado}/pagina{numero}" for numero in range(2, ultima_pagina + 1)]


def extraer_datos_publicacion(html: str, url: str) -> dict[str, Any]:
    """Extrae campos básicos desde el detalle de una publicación.

    El sitio expone un objeto estructurado dentro de ``__NEXT_DATA__``. La fuente
    principal para este scraper es ``pageProps.data`` y, si hiciera falta,
    algunos valores de ``technicalSheet`` como respaldo.
    """
    soup = BeautifulSoup(html, "html.parser")
    data = _extraer_next_data(soup)
    page_props = data.get("props", {}).get("pageProps", {}) if isinstance(data, dict) else {}
    detalle = page_props.get("data", {}) if isinstance(page_props, dict) else {}
    ficha = page_props.get("technicalSheet", []) if isinstance(page_props, dict) else []
    ficha_map = _normalizar_technical_sheet(ficha)

    titulo = _limpiar_texto(detalle.get("title") or _obtener_texto(soup, ["h1", "title"]))
    descripcion = _limpiar_texto(detalle.get("description") or _obtener_texto(soup, ["p.lc-description", "div.lc-description", "article p", "div[class*='description']"]))

    precio_texto, moneda, monto = _extraer_precio(detalle)
    barrio = _extraer_barrio(detalle, ficha_map)
    dormitorios = _extraer_campo_numerico(detalle, ficha_map, ["bedrooms", "dormitorios", "dormitorio"])
    banios = _extraer_campo_numerico(detalle, ficha_map, ["bathrooms", "baños", "banios", "banio"])
    texto_publicacion = f"{titulo} {descripcion}"
    metros_cuadrados = _extraer_metros_cuadrados(detalle, ficha_map, texto_publicacion)
    gastos_comunes = _extraer_gastos_comunes(detalle, ficha_map, texto_publicacion)
    tipo_propiedad = _extraer_tipo_propiedad(detalle, ficha_map)
    referencia = _extraer_referencia(detalle, ficha_map, url)

    return {
        "url": url,
        "titulo": titulo or None,
        "precio": precio_texto or None,
        "moneda": moneda,
        "monto": monto,
        "barrio": barrio,
        "dormitorios": dormitorios,
        "banios": banios,
        "metros_cuadrados": metros_cuadrados,
        "gastos_comunes": gastos_comunes,
        "tipo_propiedad": tipo_propiedad,
        "referencia": referencia,
        "descripcion": descripcion or None,
    }


def _extraer_next_data(soup: BeautifulSoup) -> dict[str, Any]:
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag is None or not script_tag.string:
        return {}

    try:
        return json.loads(script_tag.string)
    except json.JSONDecodeError:
        return {}


def _normalizar_technical_sheet(technical_sheet: Any) -> dict[str, str]:
    salida: dict[str, str] = {}
    if not isinstance(technical_sheet, list):
        return salida

    for item in technical_sheet:
        if not isinstance(item, dict):
            continue
        texto = _limpiar_texto(item.get("text"))
        valor = _limpiar_texto(item.get("value"))
        campo = _limpiar_texto(item.get("field"))
        if texto:
            salida[texto.lower()] = valor
        if campo:
            salida[campo.lower()] = valor
    return salida


def _obtener_texto(soup: BeautifulSoup, selectores: list[str]) -> str:
    for selector in selectores:
        elemento = soup.select_one(selector)
        if elemento:
            texto = _limpiar_texto(elemento.get_text(" ", strip=True))
            if texto:
                return texto
    return ""


def _limpiar_texto(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, str):
        texto = valor
    else:
        texto = str(valor)

    texto = unescape(texto)
    texto = re.sub(r"<\s*br\s*/?>", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return " ".join(texto.split())


def _extraer_precio(detalle: dict[str, Any]) -> tuple[str | None, str | None, int | None]:
    price = detalle.get("price") if isinstance(detalle, dict) else None
    if isinstance(price, dict):
        amount = price.get("amount")
        currency = price.get("currency", {}) if isinstance(price.get("currency"), dict) else {}
        moneda = _limpiar_texto(currency.get("name") or detalle.get("currency")) or None
        monto = int(amount) if isinstance(amount, int) else _to_int(amount)
        if monto is not None and moneda:
            return f"{moneda} {formatear_numero(monto)}", moneda, monto
        if monto is not None:
            return formatear_numero(monto), moneda, monto

    fallback = _limpiar_texto(detalle.get("price_text") or detalle.get("priceDisplay") or "")
    if fallback:
        moneda = "U$S" if "U$S" in fallback else ("$" if "$" in fallback else None)
        monto = _to_int(re.sub(r"[^0-9]", "", fallback))
        return fallback, moneda, monto

    return None, None, None


def _extraer_barrio(detalle: dict[str, Any], ficha_map: dict[str, str]) -> str | None:
    locations = detalle.get("locations", {}) if isinstance(detalle, dict) else {}
    neighborhood = locations.get("neighbourhood") if isinstance(locations, dict) else None
    if isinstance(neighborhood, list) and neighborhood:
        nombre = _limpiar_texto(neighborhood[0].get("name"))
        if nombre:
            return nombre

    for key in ("neighborhood_name", "zona", "neighbourhood_name"):
        valor = ficha_map.get(key)
        if valor:
            return valor

    address = _limpiar_texto(detalle.get("address"))
    if address:
        return address

    return None


def _extraer_campo_numerico(detalle: dict[str, Any], ficha_map: dict[str, str], keys: list[str]) -> str | None:
    for key in keys:
        valor = detalle.get(key)
        texto = _limpiar_texto(valor)
        if texto:
            return texto

    for key in keys:
        valor = ficha_map.get(key)
        if valor:
            return valor

    return None


def _extraer_metros_cuadrados(detalle: dict[str, Any], ficha_map: dict[str, str], texto_publicacion: str = "") -> str | None:
    candidatos = [
        detalle.get("m2Built"),
        detalle.get("m2"),
        detalle.get("m2Terrace"),
        detalle.get("m2Terrain"),
        detalle.get("surface"),
        detalle.get("surface_total"),
        detalle.get("surface_built"),
    ]
    for candidato in candidatos:
        texto = _limpiar_texto(candidato)
        if texto and (_to_int(texto) or 0) > 0:
            return texto

    for key in ("m² edificados", "m² de terraza", "m² del terreno", "m2built", "m2", "surface"):
        valor = ficha_map.get(key)
        if valor and (_to_int(valor) or 0) > 0:
            return valor

    metros_descripcion = _extraer_metros_desde_texto(texto_publicacion)
    if metros_descripcion is not None:
        return str(metros_descripcion)

    return None


def _extraer_gastos_comunes(detalle: dict[str, Any], ficha_map: dict[str, str], texto_publicacion: str = "") -> str | None:
    valor = detalle.get("commonExpenses")
    if isinstance(valor, dict):
        amount = valor.get("amount")
        currency = valor.get("currency", {}) if isinstance(valor.get("currency"), dict) else {}
        moneda = _limpiar_texto(currency.get("name")) or None
        monto = _to_int(amount)
        if monto is not None and monto > 0:
            return f"{moneda} {formatear_numero(monto)}" if moneda else formatear_numero(monto)

    if not isinstance(valor, dict):
        texto = _limpiar_texto(valor)
        if texto:
            return texto

    valor = _limpiar_texto(detalle.get("commonExpenses_currency"))
    if valor:
        return valor

    texto = ficha_map.get("gastos comunes") or ficha_map.get("commonexpenses")
    if texto:
        return texto

    gastos_descripcion = _extraer_gastos_desde_texto(texto_publicacion)
    return gastos_descripcion or None


def _extraer_tipo_propiedad(detalle: dict[str, Any], ficha_map: dict[str, str]) -> str | None:
    candidatos = [
        detalle.get("property_type_name"),
        detalle.get("propertyType"),
        detalle.get("property_type"),
        ficha_map.get("tipo de propiedad"),
        ficha_map.get("property_type_name"),
    ]
    for candidato in candidatos:
        if isinstance(candidato, dict):
            texto = _limpiar_texto(candidato.get("name") or candidato.get("title") or candidato.get("text"))
        else:
            texto = _limpiar_texto(candidato)
        if texto:
            return texto
    return None


def _extraer_referencia(detalle: dict[str, Any], ficha_map: dict[str, str], url: str) -> str | None:
    candidatos = [
        detalle.get("code"),
        detalle.get("code2"),
        ficha_map.get("referencia"),
        ficha_map.get("code"),
    ]
    for candidato in candidatos:
        texto = _limpiar_texto(candidato)
        if texto:
            return texto

    match = re.search(r"/(\d+)$", url)
    return match.group(1) if match else None


def _to_int(valor: Any) -> int | None:
    if valor is None:
        return None
    texto = re.sub(r"[^0-9]", "", str(valor))
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        return None


def _extraer_gastos_desde_texto(texto: str) -> str | None:
    texto = _limpiar_texto(texto)
    if not texto:
        return None

    match = re.search(
        r"gastos?\s+comunes?(?:\s+(?:estimados?|aprox(?:imados?)?))?\s*[:\-]?\s*(U\$S|\$)?\s*([0-9][0-9\.]{2,})",
        texto,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    moneda = match.group(1) or "$"
    monto = _to_int(match.group(2).replace(".", ""))
    if monto is None or monto <= 0:
        return None
    return f"{moneda} {formatear_numero(monto)}"


def _extraer_metros_desde_texto(texto: str) -> int | None:
    texto = _limpiar_texto(texto)
    if not texto:
        return None

    patrones = [
        r"(?:area|superficie|m2|m²)[^0-9]{0,20}([0-9]{2,3})(?:[,.][0-9]+)?\s*(?:m2|m²)?",
        r"([0-9]{2,3})(?:[,.][0-9]+)?\s*(?:m2|m²)",
    ]
    for patron in patrones:
        match = re.search(patron, texto, flags=re.IGNORECASE)
        if not match:
            continue
        metros = _to_int(match.group(1))
        if metros is not None and 10 <= metros <= 300:
            return metros
    return None


def formatear_numero(valor: int) -> str:
    """Formatea números con separador de miles para monedas locales."""
    return f"{valor:,}".replace(",", ".")


def _extraer_numero_pagina(href: str) -> int | None:
    match = re.search(r"/pagina(\d+)(?:$|[/?#])", href)
    if not match:
        return None
    return int(match.group(1))


def _es_link_de_publicacion(href: str) -> bool:
    """Determina si el href parece apuntar a una publicación individual."""
    partes = href.rstrip("/").split("/")
    if len(partes) < 2:
        return False

    # En InfoCasas, la ficha de una propiedad termina con un id numerico.
    return partes[-1].isdigit()
