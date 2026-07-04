"""Funciones simples para descargar HTML."""

from __future__ import annotations

import time

import requests
from requests.exceptions import ProxyError, RequestException

from config import (
    HEADERS,
    REQUEST_RETRIES,
    REQUEST_RETRY_BACKOFF_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
)


def _descargar_sin_proxy(url: str) -> str | None:
    """Segundo intento sin heredar proxies del entorno."""
    session = requests.Session()
    session.trust_env = False

    try:
        print("Reintentando sin usar proxies del entorno...")
        respuesta = session.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        respuesta.raise_for_status()
        print("Descarga correcta sin proxy.")
        return respuesta.text
    except RequestException as error:
        print(f"Error en el segundo intento: {error}")
        return None
    finally:
        session.close()


def obtener_html(url: str) -> str | None:
    """Descarga el HTML de una URL con reintentos ante errores temporales."""
    for intento in range(1, REQUEST_RETRIES + 1):
        try:
            print(f"Descargando: {url} (intento {intento}/{REQUEST_RETRIES})")
            respuesta = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            respuesta.raise_for_status()
            print("Descarga correcta.")
            return respuesta.text
        except ProxyError as error:
            print(f"Proxy del entorno no disponible: {error}")
            html = _descargar_sin_proxy(url)
            if html is not None:
                return html
        except RequestException as error:
            print(f"Error al descargar la pagina: {error}")

        if intento < REQUEST_RETRIES:
            espera = REQUEST_RETRY_BACKOFF_SECONDS * intento
            print(f"Esperando {espera} segundos antes de reintentar...")
            time.sleep(espera)

    print(f"No se pudo descargar despues de {REQUEST_RETRIES} intentos: {url}")
    return None
