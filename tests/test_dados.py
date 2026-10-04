import os
import json
import tempfile
import unittest
from pathlib import Path
import sys

# Garante que o diretório raiz esteja no sys.path para importação dos módulos
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dados import carregar_dados, salvar_dados, ARQUIVO_DADOS


class TestDados(unittest.TestCase):
    """Suíte de testes para as funções de manipulação e persistência de dados (dados.py)."""

    def setUp(self):
        """Cria um ambiente temporário isolado antes de cada teste."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)
        self.test_file = self.tmp_path / "test_dados.json"

    def tearDown(self):
        """Limpa o diretório temporário após a execução de cada teste."""
        self.temp_dir.cleanup()

    def test_carregar_dados_arquivo_inexistente(self):
        """
        Deve inicializar uma estrutura padrão segura {'maquinas': []} e salvar o arquivo
        quando o caminho especificado não existir previamente.
        """
        caminho = str(self.test_file)
        self.assertFalse(os.path.exists(caminho))

        dados = carregar_dados(caminho)

        # Verifica o retorno
        self.assertEqual(dados, {"maquinas": []})

        # Verifica se o arquivo foi realmente criado no disco
        self.assertTrue(os.path.exists(caminho))
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo_salvo = json.load(f)
        self.assertEqual(conteudo_salvo, {"maquinas": []})

    def test_carregar_dados_arquivo_existente_valido(self):
        """
        Deve carregar com sucesso as informações de máquinas a partir de um arquivo JSON válido.
        """
        conteudo_esperado = {
            "maquinas": [
                {
                    "id": 1,
                    "nome": "Torno CNC 01",
                    "status": "normal",
                    "historico": [
                        {
                            "timestamp": "2026-10-04 10:00:00",
                            "temperatura": 62.5,
                            "vibracao": 3.2,
                            "consumo": 310.0
                        }
                    ]
                },
                {
                    "id": 2,
                    "nome": "Fresadora Universal 02",
                    "status": "sem dados",
                    "historico": []
                }
            ]
        }
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(conteudo_esperado, f, indent=4, ensure_ascii=False)

        dados = carregar_dados(str(self.test_file))

        self.assertEqual(dados, conteudo_esperado)
        self.assertEqual(len(dados["maquinas"]), 2)
        self.assertEqual(dados["maquinas"][0]["nome"], "Torno CNC 01")
        self.assertEqual(dados["maquinas"][1]["nome"], "Fresadora Universal 02")

    def test_carregar_dados_arquivo_corrompido(self):
        """
        Deve se recuperar com segurança caso o arquivo JSON esteja corrompido:
        - Não deve quebrar com exceção (JSONDecodeError/UnicodeDecodeError).
        - Deve gerar um arquivo de backup '.corrompido.bak'.
        - Deve redefinir o arquivo para a estrutura padrão segura {'maquinas': []}.
        - Deve retornar a estrutura padrão segura.
        """
        caminho = str(self.test_file)
        conteudo_corrompido = "{ 'invalido': True, erro_sintaxe: [1, 2, "
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo_corrompido)

        dados = carregar_dados(caminho)

        # Retorno seguro
        self.assertEqual(dados, {"maquinas": []})

        # Arquivo principal foi restaurado
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo_restaurado = json.load(f)
        self.assertEqual(conteudo_restaurado, {"maquinas": []})

        # Backup foi criado e contém o conteúdo corrompido original
        caminho_backup = f"{caminho}.corrompido.bak"
        self.assertTrue(os.path.exists(caminho_backup), "O arquivo de backup deveria ter sido criado.")
        with open(caminho_backup, "r", encoding="utf-8") as f:
            conteudo_backup = f.read()
        self.assertEqual(conteudo_backup, conteudo_corrompido)

    def test_salvar_dados_sucesso(self):
        """
        Deve salvar os dados atômica e corretamente em disco no formato JSON com formatação UTF-8.
        """
        caminho = str(self.test_file)
        dados = {
            "maquinas": [
                {
                    "id": 1,
                    "nome": "Prensa Hidráulica 01",
                    "status": "normal",
                    "historico": []
                }
            ]
        }

        salvar_dados(dados, caminho)

        # Arquivo deve existir
        self.assertTrue(os.path.exists(caminho))

        # Arquivo temporário intermediário .tmp não deve permanecer
        self.assertFalse(os.path.exists(f"{caminho}.tmp"))

        # Leitura e verificação do conteúdo gravado
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo_salvo = json.load(f)
        self.assertEqual(conteudo_salvo, dados)
        self.assertEqual(conteudo_salvo["maquinas"][0]["nome"], "Prensa Hidráulica 01")

    def test_isolamento_sem_alterar_producao(self):
        """
        Garante que a execução com caminhos temporários não altera em hipótese alguma o dados.json de produção.
        """
        arquivo_prod = BASE_DIR / ARQUIVO_DADOS
        if arquivo_prod.exists():
            mtime_antes = arquivo_prod.stat().st_mtime
            tamanho_antes = arquivo_prod.stat().st_size

            # Executa ações em arquivo temporário
            temp_path = str(self.tmp_path / "isolado.json")
            salvar_dados({"maquinas": [{"id": 999, "nome": "Teste Isolado"}]}, temp_path)
            carregar_dados(temp_path)

            mtime_depois = arquivo_prod.stat().st_mtime
            tamanho_depois = arquivo_prod.stat().st_size

            self.assertEqual(mtime_antes, mtime_depois, "O arquivo de produção não deve ser modificado.")
            self.assertEqual(tamanho_antes, tamanho_depois, "O tamanho do arquivo de produção deve permanecer inalterado.")


if __name__ == "__main__":
    unittest.main()
