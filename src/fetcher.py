"""Funciones simples para descargar HTML."""

from __future__ import annotations

import requests
from requests.exceptions import ProxyError, RequestException

from config import HEADERS, REQUEST_TIMEOUT_SECONDS


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
    """Descarga el HTML de una URL y devuelve su texto.

    Si ocurre un error de red o la respuesta no es válida,
    devuelve None.
    """
    try:
        print(f"Descargando: {url}")
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
        return _descargar_sin_proxy(url)
    except RequestException as error:
        print(f"Error al descargar la página: {error}")
        return None
