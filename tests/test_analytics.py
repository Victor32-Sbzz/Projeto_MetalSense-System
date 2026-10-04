import unittest
from analytics import (
    calcular_estatisticas,
    calcular_tendencia,
    diagnosticar_causa_raiz,
    calcular_indice_saude
)


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.historico_normal = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 58.0, "vibracao": 3.0, "consumo": 300.0},
            {"timestamp": "2026-10-04 10:05:00", "temperatura": 59.0, "vibracao": 3.1, "consumo": 305.0},
            {"timestamp": "2026-10-04 10:10:00", "temperatura": 58.5, "vibracao": 2.9, "consumo": 298.0},
            {"timestamp": "2026-10-04 10:15:00", "temperatura": 60.0, "vibracao": 3.2, "consumo": 310.0},
        ]

    def test_calcular_estatisticas_com_dados(self):
        stats = calcular_estatisticas(self.historico_normal, "temperatura")
        self.assertAlmostEqual(stats["media"], 58.88, places=1)
        self.assertEqual(stats["min"], 58.0)
        self.assertEqual(stats["max"], 60.0)
        self.assertEqual(stats["ultima"], 60.0)

    def test_calcular_estatisticas_sem_dados(self):
        stats = calcular_estatisticas([], "temperatura")
        self.assertEqual(stats["media"], 0.0)
        self.assertEqual(stats["desvio"], 0.0)

    def test_calcular_tendencia_estavel(self):
        tend = calcular_tendencia(self.historico_normal, "temperatura")
        self.assertIn(tend, ["Estável", "Leve Subida"])

    def test_calcular_tendencia_aquecimento_acelerado(self):
        historico_aquecendo = [
            {"temperatura": 55.0},
            {"temperatura": 58.0},
            {"temperatura": 62.0},
            {"temperatura": 68.0},
            {"temperatura": 75.0},
        ]
        tend = calcular_tendencia(historico_aquecendo, "temperatura")
        self.assertEqual(tend, "Crescente Acelerada")

    def test_diagnosticar_causa_raiz_rolamento(self):
        ultima = {"temperatura": 82.0, "vibracao": 9.5, "consumo": 320.0}
        hipoteses = diagnosticar_causa_raiz(ultima, {"temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0})
        self.assertTrue(any("FALHA MECÂNICA GRAVE" in h for h in hipoteses))

    def test_diagnosticar_causa_raiz_desalinhamento(self):
        ultima = {"temperatura": 65.0, "vibracao": 7.5, "consumo": 300.0}
        hipoteses = diagnosticar_causa_raiz(ultima, {"temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0})
        self.assertTrue(any("DESALINHAMENTO" in h for h in hipoteses))

    def test_calcular_indice_saude_normal(self):
        saude = calcular_indice_saude(self.historico_normal)
        self.assertGreaterEqual(saude["score"], 85.0)
        self.assertIn("Excelente", saude["classificacao"])

    def test_calcular_indice_saude_critico(self):
        historico_critico = self.historico_normal + [
            {"timestamp": "2026-10-04 10:20:00", "temperatura": 95.0, "vibracao": 14.0, "consumo": 620.0}
        ]
        saude = calcular_indice_saude(historico_critico)
        self.assertLess(saude["score"], 50.0)
        self.assertIn("Crítico", saude["classificacao"])


if __name__ == "__main__":
    unittest.main()
