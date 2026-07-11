import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from parser import extraer_datos_publicacion


class ParserTests(unittest.TestCase):
    def test_limpia_html_y_extrae_fallbacks_desde_descripcion(self):
        payload = {
            "props": {
                "pageProps": {
                    "data": {
                        "title": "Apartamento prueba",
                        "description": "Area interna 43 m²<br>Gastos comunes estimados: $4.500&nbsp;mensuales",
                        "price": {"amount": 30000, "currency": {"name": "$"}},
                        "locations": {"neighbourhood": [{"name": "Cordón"}]},
                        "bedrooms": 1,
                        "bathrooms": 1,
                        "m2Built": 0,
                        "commonExpenses": {"amount": 0, "currency": {"name": "$"}},
                        "property_type_name": "Apartamento",
                    },
                    "technicalSheet": [],
                }
            }
        }
        html = f'<html><script id="__NEXT_DATA__">{json.dumps(payload)}</script></html>'

        fila = extraer_datos_publicacion(html, "https://www.infocasas.com.uy/test/123")

        self.assertEqual(fila["descripcion"], "Area interna 43 m² Gastos comunes estimados: $4.500 mensuales")
        self.assertEqual(fila["metros_cuadrados"], "43")
        self.assertEqual(fila["gastos_comunes"], "$ 4.500")


if __name__ == "__main__":
    unittest.main()
