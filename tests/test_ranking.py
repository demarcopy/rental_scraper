import sys
import unittest
from pathlib import Path

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ranking import _calcular_score, _preparar_datos


class RankingTests(unittest.TestCase):
    def test_calcular_score_es_defensivo_y_penaliza_baja_calidad(self):
        df = pd.DataFrame(
            [
                {
                    "url": f"https://example.com/{i}",
                    "titulo": "Apartamento con garaje",
                    "descripcion": "Buen estado",
                    "precio": f"$ {30000 + i * 1000}",
                    "moneda": "$",
                    "monto": 30000 + i * 1000,
                    "barrio": "Cordón",
                    "dormitorios": 1,
                    "banios": 1,
                    "metros_cuadrados": 40 if i != 4 else None,
                    "gastos_comunes": "$ 3.000" if i != 4 else None,
                    "tipo_propiedad": "Apartamento",
                    "referencia": str(i),
                }
                for i in range(5)
            ]
        )

        preparado = _preparar_datos(df)
        scored = _calcular_score(preparado)

        self.assertEqual(len(scored), 5)
        self.assertIn("score_oportunidad", scored.columns)
        self.assertIn("data_quality_score", scored.columns)
        self.assertLess(scored.loc[scored["url"] == "https://example.com/4", "data_quality_score"].iloc[0], 100)


if __name__ == "__main__":
    unittest.main()
