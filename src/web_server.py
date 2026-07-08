"""Servidor local para explorar el ranking de alquileres."""

from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ranking import cargar_ranking


class RentalRankingHandler(SimpleHTTPRequestHandler):
    """Sirve la SPA y expone los datos del ranking como JSON."""

    raiz_proyecto: Path


    def __init__(self, *args, directory: str | None = None, **kwargs) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        ruta = urlparse(self.path).path
        if ruta == "/api/rentals":
            self._responder_ranking()
            return
        if ruta == "/" or ruta.startswith("/assets/"):
            super().do_GET()
            return
        self.path = "/"
        super().do_GET()

    def _responder_ranking(self) -> None:
        try:
            payload = cargar_ranking(self.raiz_proyecto)
            contenido = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
        except FileNotFoundError as exc:
            contenido = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(404)
        except Exception as exc:  # pragma: no cover - defensa para errores visibles en el navegador.
            contenido = json.dumps({"error": f"No se pudo calcular el ranking: {exc}"}, ensure_ascii=False).encode("utf-8")
            self.send_response(500)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)


def main() -> None:
    parser = argparse.ArgumentParser(description="Levanta la SPA del ranking de alquileres.")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor local.")
    parser.add_argument("--port", default=8000, type=int, help="Puerto del servidor local.")
    args = parser.parse_args()

    raiz_proyecto = Path(__file__).resolve().parents[1]
    web_dir = raiz_proyecto / "web"
    if not web_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta web: {web_dir}")

    RentalRankingHandler.raiz_proyecto = raiz_proyecto
    server = ThreadingHTTPServer(
        (args.host, args.port),
        lambda *handler_args, **handler_kwargs: RentalRankingHandler(
            *handler_args,
            directory=str(web_dir),
            **handler_kwargs,
        ),
    )

    print(f"Ranking disponible en http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
