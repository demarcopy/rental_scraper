"""Configuracion basica del scraper."""

from __future__ import annotations

import os

BASE_URL = "https://www.infocasas.com.uy/alquiler/inmuebles/1-dormitorio"

HEADERS = {
    # Header simple para simular una navegacion normal.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

# Pausa entre requests. Al recorrer todas las paginas conviene priorizar estabilidad.
REQUEST_DELAY_SECONDS = 2

# Tiempo maximo de espera para cada request.
REQUEST_TIMEOUT_SECONDS = 30

# Cantidad de reintentos ante timeouts o errores temporales.
REQUEST_RETRIES = 3

# Espera base entre reintentos; se multiplica por el numero de intento.
REQUEST_RETRY_BACKOFF_SECONDS = 5

# Por defecto el scraper no guarda HTML crudo para evitar peso innecesario.
# Para depurar parsing se puede ejecutar con CACHE_RAW_HTML=1.
CACHE_RAW_HTML = os.getenv("CACHE_RAW_HTML", "0") == "1"
