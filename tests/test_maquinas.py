import unittest
from unittest.mock import patch
from datetime import datetime
from pathlib import Path
import sys

# Garante que o diretório raiz esteja no sys.path para importação dos módulos
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from maquinas import (
    criar_maquina,
    remover_maquina,
    simular_leitura,
    analisar_maquina,
    registrar_leitura,
)


class TestMaquinas(unittest.TestCase):
    """Suíte de testes para a lógica pura de gerenciamento e telemetria de máquinas (maquinas.py)."""

    def setUp(self):
        """
        Executado antes de cada teste.
        Aplica mock em salvar_dados para isolar completamente os testes de I/O em disco
        e proteger o arquivo dados.json de produção.
        """
        self.patcher = patch("maquinas.salvar_dados")
        self.mock_salvar_dados = self.patcher.start()

        # Dicionário de dados base limpo para os testes
        self.dados_base = {
            "maquinas": []
        }

    def tearDown(self):
        """Finaliza os patches após cada teste."""
        self.patcher.stop()

    # --------------------------------------------------------------------------
    # 1. Testes de criar_maquina
    # --------------------------------------------------------------------------

    def test_criar_maquina_com_sucesso(self):
        """Deve criar uma nova máquina com id=1, campos corretos e chamar salvar_dados."""
        maquina = criar_maquina(self.dados_base, "Torno Mecânico 01")

        self.assertEqual(maquina["id"], 1)
        self.assertEqual(maquina["nome"], "Torno Mecânico 01")
        self.assertEqual(maquina["status"], "sem dados")
        self.assertEqual(maquina["historico"], [])

        # Deve ter sido adicionada à lista
        self.assertIn(maquina, self.dados_base["maquinas"])
        self.assertEqual(len(self.dados_base["maquinas"]), 1)

        # Deve persistir os dados
        self.mock_salvar_dados.assert_called_once_with(self.dados_base)

    def test_criar_maquina_limpeza_espacos_nome(self):
        """Deve aplicar strip no nome da máquina ao criá-la."""
        maquina = criar_maquina(self.dados_base, "   Fresadora CNC   ")
        self.assertEqual(maquina["nome"], "Fresadora CNC")

    def test_criar_maquina_inicializa_chave_maquinas_se_ausente(self):
        """Deve criar a chave 'maquinas' caso ela não exista no dicionário de dados."""
        dados_vazio = {}
        maquina = criar_maquina(dados_vazio, "Prensa 01")
        self.assertIn("maquinas", dados_vazio)
        self.assertEqual(dados_vazio["maquinas"], [maquina])

    def test_criar_maquina_geracao_ids_incrementais(self):
        """Deve gerar IDs incrementais corretamente (max(ids) + 1)."""
        m1 = criar_maquina(self.dados_base, "Máquina 1")
        m2 = criar_maquina(self.dados_base, "Máquina 2")
        m3 = criar_maquina(self.dados_base, "Máquina 3")

        self.assertEqual(m1["id"], 1)
        self.assertEqual(m2["id"], 2)
        self.assertEqual(m3["id"], 3)

        # Se houver IDs não sequenciais
        dados_esparsos = {
            "maquinas": [
                {"id": 5, "nome": "M5", "status": "sem dados", "historico": []},
                {"id": 12, "nome": "M12", "status": "sem dados", "historico": []},
            ]
        }
        m_nova = criar_maquina(dados_esparsos, "M13")
        self.assertEqual(m_nova["id"], 13)

    def test_criar_maquina_nome_vazio_ou_apenas_espacos(self):
        """Deve lançar ValueError se o nome for vazio ou contiver apenas espaços em branco."""
        casos_invalidos = ["", "   ", "\t", "\n  \t  ", "           "]
        for nome_invalido in casos_invalidos:
            with self.subTest(nome=repr(nome_invalido)):
                with self.assertRaises(ValueError) as ctx:
                    criar_maquina(self.dados_base, nome_invalido)
                self.assertIn("O nome da máquina não pode ser vazio.", str(ctx.exception))

    # --------------------------------------------------------------------------
    # 2. Testes de remover_maquina
    # --------------------------------------------------------------------------

    def test_remover_maquina_existente(self):
        """Deve remover a máquina do dicionário, chamar salvar_dados e retornar True."""
        criar_maquina(self.dados_base, "Máquina A")
        criar_maquina(self.dados_base, "Máquina B")
        self.mock_salvar_dados.reset_mock()

        removido = remover_maquina(self.dados_base, 1)

        self.assertTrue(removido)
        self.assertEqual(len(self.dados_base["maquinas"]), 1)
        self.assertEqual(self.dados_base["maquinas"][0]["id"], 2)
        self.mock_salvar_dados.assert_called_once_with(self.dados_base)

    def test_remover_maquina_inexistente(self):
        """Deve retornar False e não chamar salvar_dados se o ID não existir."""
        criar_maquina(self.dados_base, "Máquina A")
        self.mock_salvar_dados.reset_mock()

        removido = remover_maquina(self.dados_base, 999)

        self.assertFalse(removido)
        self.assertEqual(len(self.dados_base["maquinas"]), 1)
        self.mock_salvar_dados.assert_not_called()

    # --------------------------------------------------------------------------
    # 3. Testes de simular_leitura
    # --------------------------------------------------------------------------

    def test_simular_leitura_modo_normal(self):
        """Deve retornar leitura com campos válidos dentro dos limites normais."""
        for _ in range(20):
            leitura = simular_leitura(gerar_anomalia=False)

            # Verifica presença de todas as chaves obrigatórias
            self.assertIn("timestamp", leitura)
            self.assertIn("temperatura", leitura)
            self.assertIn("vibracao", leitura)
            self.assertIn("consumo", leitura)

            # Valida formato de timestamp
            dt = datetime.strptime(leitura["timestamp"], "%Y-%m-%d %H:%M:%S")
            self.assertIsInstance(dt, datetime)

            # Valida faixas operacionais normais
            self.assertGreaterEqual(leitura["temperatura"], 55.0)
            self.assertLessEqual(leitura["temperatura"], 68.0)

            self.assertGreaterEqual(leitura["vibracao"], 2.0)
            self.assertLessEqual(leitura["vibracao"], 4.5)

            self.assertGreaterEqual(leitura["consumo"], 250.0)
            self.assertLessEqual(leitura["consumo"], 380.0)

    def test_simular_leitura_modo_anomalia(self):
        """Deve retornar campos válidos ao gerar anomalia e gerar métricas anômalas."""
        gerou_anomalia_detectavel = False
        for _ in range(50):
            leitura = simular_leitura(gerar_anomalia=True)

            self.assertIn("timestamp", leitura)
            self.assertIn("temperatura", leitura)
            self.assertIn("vibracao", leitura)
            self.assertIn("consumo", leitura)

            self.assertIsInstance(leitura["temperatura"], (int, float))
            self.assertIsInstance(leitura["vibracao"], (int, float))
            self.assertIsInstance(leitura["consumo"], (int, float))

            # Verifica se pelo menos uma métrica atinge nível crítico
            if leitura["temperatura"] > 85.0 or leitura["vibracao"] > 8.0 or leitura["consumo"] > 500.0:
                gerou_anomalia_detectavel = True

        self.assertTrue(gerou_anomalia_detectavel, "Deveria ter gerado pelo menos uma anomalia detectável.")

    # --------------------------------------------------------------------------
    # 4. Testes de analisar_maquina
    # --------------------------------------------------------------------------

    def test_analisar_maquina_id_inexistente(self):
        """Deve retornar 'ID não encontrado...' quando a máquina não existir."""
        resultado = analisar_maquina(self.dados_base, 999)
        self.assertEqual(resultado, "ID não encontrado...")

    def test_analisar_maquina_historico_insuficiente(self):
        """
        Deve indicar histórico insuficiente e definir status 'sem dados'
        quando houver menos de 2 leituras (0 ou 1 leitura).
        """
        maquina = criar_maquina(self.dados_base, "Torno Teste")

        # Caso 1: 0 leituras
        res_0 = analisar_maquina(self.dados_base, maquina["id"])
        self.assertEqual(
            res_0,
            "Histórico insuficiente para análise (mínimo de 2 medições necessárias)."
        )
        self.assertEqual(maquina["status"], "sem dados")

        # Caso 2: 1 leitura
        maquina["historico"].append({
            "timestamp": "2026-10-04 10:00:00",
            "temperatura": 60.0,
            "vibracao": 3.0,
            "consumo": 300.0
        })
        res_1 = analisar_maquina(self.dados_base, maquina["id"])
        self.assertEqual(
            res_1,
            "Histórico insuficiente para análise (mínimo de 2 medições necessárias)."
        )
        self.assertEqual(maquina["status"], "sem dados")

    def test_analisar_maquina_comportamento_normal(self):
        """Deve identificar comportamento normal e definir status 'normal' para histórico estável."""
        maquina = criar_maquina(self.dados_base, "Fresadora Teste")
        maquina["historico"] = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0},
            {"timestamp": "2026-10-04 10:01:00", "temperatura": 61.0, "vibracao": 3.2, "consumo": 310.0}
        ]

        resultado = analisar_maquina(self.dados_base, maquina["id"])

        self.assertEqual(resultado, "Comportamento dentro do padrão operacional normal!")
        self.assertEqual(maquina["status"], "normal")

    def test_analisar_maquina_anomalia_temperatura_critica(self):
        """Deve detectar anomalia crítica de temperatura (> 85°C) e definir status 'anomalia'."""
        maquina = criar_maquina(self.dados_base, "Extrusora 01")
        maquina["historico"] = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0},
            {"timestamp": "2026-10-04 10:01:00", "temperatura": 92.5, "vibracao": 3.0, "consumo": 300.0}
        ]

        resultado = analisar_maquina(self.dados_base, maquina["id"])

        self.assertIn("Possível anomalia detectada:", resultado)
        self.assertIn("Temperatura crítica (92.5°C)", resultado)
        self.assertEqual(maquina["status"], "anomalia")

    def test_analisar_maquina_anomalia_vibracao_critica(self):
        """Deve detectar anomalia crítica de vibração (> 8.0 mm/s) e definir status 'anomalia'."""
        maquina = criar_maquina(self.dados_base, "Compressor 01")
        maquina["historico"] = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0},
            {"timestamp": "2026-10-04 10:01:00", "temperatura": 62.0, "vibracao": 11.4, "consumo": 300.0}
        ]

        resultado = analisar_maquina(self.dados_base, maquina["id"])

        self.assertIn("Possível anomalia detectada:", resultado)
        self.assertIn("Vibração excessiva (11.4 mm/s)", resultado)
        self.assertEqual(maquina["status"], "anomalia")

    def test_analisar_maquina_anomalia_consumo_critico(self):
        """Deve detectar anomalia crítica de consumo elétrico (> 500 W) e definir status 'anomalia'."""
        maquina = criar_maquina(self.dados_base, "Motor Trifásico 01")
        maquina["historico"] = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0},
            {"timestamp": "2026-10-04 10:01:00", "temperatura": 62.0, "vibracao": 3.1, "consumo": 650.0}
        ]

        resultado = analisar_maquina(self.dados_base, maquina["id"])

        self.assertIn("Possível anomalia detectada:", resultado)
        self.assertIn("Consumo elétrico anormal (650.0 W)", resultado)
        self.assertEqual(maquina["status"], "anomalia")

    def test_analisar_maquina_multiplas_anomalias_criticas(self):
        """Deve detectar múltiplas anomalias críticas simultaneamente."""
        maquina = criar_maquina(self.dados_base, "Caldeira 01")
        maquina["historico"] = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0},
            {"timestamp": "2026-10-04 10:01:00", "temperatura": 95.0, "vibracao": 12.0, "consumo": 700.0}
        ]

        resultado = analisar_maquina(self.dados_base, maquina["id"])

        self.assertIn("Temperatura crítica (95.0°C)", resultado)
        self.assertIn("Vibração excessiva (12.0 mm/s)", resultado)
        self.assertIn("Consumo elétrico anormal (700.0 W)", resultado)
        self.assertEqual(maquina["status"], "anomalia")

    def test_analisar_maquina_anomalia_estatistica_historico(self):
        """
        Deve detectar anomalia por desvio estatístico (> 2.5 * desvio)
        mesmo quando os valores absolutos não ultrapassaram os limites críticos absolutos.
        """
        maquina = criar_maquina(self.dados_base, "Bancada de Precisão")
        # Baseline muito estável (desvio pequeno mas > 0.05)
        maquina["historico"] = [
            {"timestamp": "2026-10-04 10:00:00", "temperatura": 58.0, "vibracao": 2.5, "consumo": 280.0},
            {"timestamp": "2026-10-04 10:01:00", "temperatura": 58.2, "vibracao": 2.5, "consumo": 280.0},
            {"timestamp": "2026-10-04 10:02:00", "temperatura": 58.1, "vibracao": 2.5, "consumo": 280.0},
            # Salto repentino de temperatura para 65°C (abaixo do crítico 85°C, mas muito longe da média 58.1°C)
            {"timestamp": "2026-10-04 10:03:00", "temperatura": 65.0, "vibracao": 2.5, "consumo": 280.0},
        ]

        resultado = analisar_maquina(self.dados_base, maquina["id"])

        self.assertIn("Possível anomalia detectada:", resultado)
        self.assertIn("Temperatura fora do padrão histórico", resultado)
        self.assertEqual(maquina["status"], "anomalia")

    # --------------------------------------------------------------------------
    # 5. Testes de registrar_leitura
    # --------------------------------------------------------------------------

    def test_registrar_leitura_id_inexistente(self):
        """Deve retornar 'ID não encontrado...' ao registrar leitura para máquina inexistente."""
        resultado = registrar_leitura(self.dados_base, 999)
        self.assertEqual(resultado, "ID não encontrado...")

    def test_registrar_leitura_manual_com_timestamp(self):
        """Deve adicionar a leitura fornecida manualmente e executar a análise com sucesso."""
        maquina = criar_maquina(self.dados_base, "Furadeira 01")
        leitura_1 = {"timestamp": "2026-10-04 10:00:00", "temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0}
        leitura_2 = {"timestamp": "2026-10-04 10:01:00", "temperatura": 61.0, "vibracao": 3.1, "consumo": 305.0}

        # Primeira leitura
        res1 = registrar_leitura(self.dados_base, maquina["id"], leitura=leitura_1)
        self.assertEqual(len(maquina["historico"]), 1)
        self.assertEqual(res1, "Histórico insuficiente para análise (mínimo de 2 medições necessárias).")
        self.assertEqual(maquina["status"], "sem dados")

        # Segunda leitura
        res2 = registrar_leitura(self.dados_base, maquina["id"], leitura=leitura_2)
        self.assertEqual(len(maquina["historico"]), 2)
        self.assertEqual(res2, "Comportamento dentro do padrão operacional normal!")
        self.assertEqual(maquina["status"], "normal")

    def test_registrar_leitura_gera_timestamp_se_ausente(self):
        """Deve preencher automaticamente a chave 'timestamp' se ela for omitida na leitura."""
        maquina = criar_maquina(self.dados_base, "Furadeira 02")
        leitura_sem_ts = {"temperatura": 60.0, "vibracao": 3.0, "consumo": 300.0}

        registrar_leitura(self.dados_base, maquina["id"], leitura=leitura_sem_ts)

        self.assertEqual(len(maquina["historico"]), 1)
        self.assertIn("timestamp", maquina["historico"][0])
        dt = datetime.strptime(maquina["historico"][0]["timestamp"], "%Y-%m-%d %H:%M:%S")
        self.assertIsInstance(dt, datetime)

    def test_registrar_leitura_simulada_automatica(self):
        """Deve simular leitura automaticamente quando leitura=None."""
        maquina = criar_maquina(self.dados_base, "Injetora 01")

        # Primeira leitura automática
        registrar_leitura(self.dados_base, maquina["id"], leitura=None, gerar_anomalia=False)
        self.assertEqual(len(maquina["historico"]), 1)

        # Segunda leitura automática
        registrar_leitura(self.dados_base, maquina["id"], leitura=None, gerar_anomalia=False)
        self.assertEqual(len(maquina["historico"]), 2)
        self.assertEqual(maquina["status"], "normal")


if __name__ == "__main__":
    unittest.main()
