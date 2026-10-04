import unittest
import os
import tempfile
from simulador_iot import gerar_leitura_cenario, CENARIOS
from relatorios import exportar_historico_csv, gerar_ordem_servico_texto, gerar_relatorio_html
from api import app


class TestRelatoriosSimuladorAPI(unittest.TestCase):
    def setUp(self):
        self.maquina_teste = {
            "id": 99,
            "nome": "Torno CNC Teste",
            "status": "normal",
            "historico": [
                {"timestamp": "2026-10-04 12:00:00", "temperatura": 59.0, "vibracao": 3.0, "consumo": 300.0},
                {"timestamp": "2026-10-04 12:05:00", "temperatura": 60.5, "vibracao": 3.2, "consumo": 305.0},
            ]
        }
        self.api_client = app.test_client()

    def test_gerar_leitura_cenarios(self):
        for cenario in CENARIOS:
            leitura = gerar_leitura_cenario(cenario, ciclo=2)
            self.assertIn("timestamp", leitura)
            self.assertIn("temperatura", leitura)
            self.assertIn("vibracao", leitura)
            self.assertIn("consumo", leitura)
            self.assertGreater(leitura["temperatura"], 0)

    def test_exportar_csv_e_html(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "teste.csv")
            html_path = os.path.join(tmp_dir, "teste.html")

            ret_csv = exportar_historico_csv(self.maquina_teste, caminho_destino=csv_path)
            self.assertTrue(os.path.exists(ret_csv))

            ret_html = gerar_relatorio_html(self.maquina_teste, caminho_arquivo=html_path)
            self.assertTrue(os.path.exists(ret_html))

            # Verifica Ordem de Serviço
            os_txt = gerar_ordem_servico_texto(self.maquina_teste)
            self.assertIn("ORDEM DE SERVIÇO", os_txt)
            self.assertIn("Torno CNC Teste", os_txt)

    def test_api_healthcheck(self):
        resp = self.api_client.get("/health")
        self.assertEqual(resp.status_code, 200)
        dados = resp.get_json()
        self.assertEqual(dados["status"], "online")

    def test_api_listar_maquinas(self):
        resp = self.api_client.get("/api/maquinas")
        self.assertEqual(resp.status_code, 200)
        dados = resp.get_json()
        self.assertIn("maquinas", dados)


if __name__ == "__main__":
    unittest.main()
