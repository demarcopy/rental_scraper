"""Configuración básica del scraper."""

BASE_URL = "https://www.infocasas.com.uy/alquiler/inmuebles/1-dormitorio"

HEADERS = {
    # Header simple para simular una navegación normal.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

# Pausa pensada para etapas futuras con varias requests.
REQUEST_DELAY_SECONDS = 1

# Tiempo máximo de espera para cada request.
REQUEST_TIMEOUT_SECONDS = 20
