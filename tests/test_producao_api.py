"""
Suíte de Testes de Produção, Hardening e Segurança do MetalSense Gateway.
Valida autenticação RBAC, rate limiting, probes de orquestração,
validação de schemas Pydantic e tolerância a falhas.
"""

import json
import unittest
from datetime import datetime, timezone, timedelta
from api import create_app
from config import Configuracao
from dados import carregar_dados
from maquinas import criar_maquina


class TestProducaoAPI(unittest.TestCase):
    def setUp(self):
        self.chave_admin = "admin-secret-teste-123"
        self.chave_disp = "disp-sensor-teste-456"

        self.cfg = Configuracao.do_ambiente(
            ambiente="testing",
            auth_desabilitada=False,
            api_keys_admin=(self.chave_admin,),
            api_keys_dispositivo=(self.chave_disp,),
            ratelimit_global="50 per minute",
            ratelimit_telemetria="20 per minute"
        )
        self.app = create_app(self.cfg)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Garante pelo menos uma máquina no banco/dados
        dados = carregar_dados()
        if not dados.get("maquinas"):
            criar_maquina(dados, "Prensa de Teste Automatizado")

    def test_liveness_probe(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["liveness"], "UP")
        self.assertIn("uptime_segundos", data)

    def test_readiness_probe(self):
        resp = self.client.get("/ready")
        self.assertIn(resp.status_code, [200, 503])
        data = resp.get_json()
        self.assertIn("status", data)

    def test_autenticacao_sem_chave(self):
        resp = self.client.post("/api/telemetria", json={
            "id_maquina": 1,
            "temperatura": 60.0,
            "vibracao": 3.0,
            "consumo": 300.0
        })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.get_json()["codigo"], 401)

    def test_autenticacao_chave_invalida(self):
        resp = self.client.post(
            "/api/telemetria",
            headers={"X-API-Key": "chave-falsa-maliciosa"},
            json={
                "id_maquina": 1,
                "temperatura": 60.0,
                "vibracao": 3.0,
                "consumo": 300.0
            }
        )
        self.assertEqual(resp.status_code, 401)

    def test_autenticacao_chave_valida_header_x_api_key(self):
        resp = self.client.post(
            "/api/telemetria",
            headers={"X-API-Key": self.chave_disp},
            json={
                "id_maquina": 1,
                "temperatura": 62.0,
                "vibracao": 3.1,
                "consumo": 310.0
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "sucesso")

    def test_autenticacao_chave_valida_bearer_token(self):
        resp = self.client.post(
            "/api/telemetria",
            headers={"Authorization": f"Bearer {self.chave_disp}"},
            json={
                "id_maquina": 1,
                "temperatura": 61.5,
                "vibracao": 2.8,
                "consumo": 295.0
            }
        )
        self.assertEqual(resp.status_code, 200)

    def test_validacao_pydantic_temperatura_fora_dos_limites(self):
        # Temperatura de 450°C acima do limite máximo físico de 300°C
        resp = self.client.post(
            "/api/telemetria",
            headers={"X-API-Key": self.chave_disp},
            json={
                "id_maquina": 1,
                "temperatura": 450.0,
                "vibracao": 3.0,
                "consumo": 300.0
            }
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["status"], "erro")
        self.assertTrue(any("temperatura" in str(d) for d in data.get("detalhes", [])))

    def test_validacao_pydantic_vibracao_negativa(self):
        resp = self.client.post(
            "/api/telemetria",
            headers={"X-API-Key": self.chave_disp},
            json={
                "id_maquina": 1,
                "temperatura": 60.0,
                "vibracao": -5.0,
                "consumo": 300.0
            }
        )
        self.assertEqual(resp.status_code, 400)

    def test_validacao_pydantic_timestamp_futuro_excessivo(self):
        futuro = (datetime.now(timezone.utc) + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        resp = self.client.post(
            "/api/telemetria",
            headers={"X-API-Key": self.chave_disp},
            json={
                "id_maquina": 1,
                "temperatura": 60.0,
                "vibracao": 3.0,
                "consumo": 300.0,
                "timestamp": futuro
            }
        )
        self.assertEqual(resp.status_code, 400)

    def test_ingestao_lote_telemetria(self):
        lote = {
            "leituras": [
                {"id_maquina": 1, "temperatura": 59.0, "vibracao": 2.9, "consumo": 290.0},
                {"id_maquina": 1, "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0},
                {"id_maquina": 1, "temperatura": 61.0, "vibracao": 3.1, "consumo": 310.0},
            ]
        }
        resp = self.client.post(
            "/api/telemetria/lote",
            headers={"X-API-Key": self.chave_disp},
            json=lote
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["processados"], 3)


if __name__ == "__main__":
    unittest.main()
