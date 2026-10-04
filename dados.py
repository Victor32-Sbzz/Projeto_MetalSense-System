import json
import os
import shutil

ARQUIVO_DADOS = "dados.json"

def carregar_dados(caminho_arquivo: str = ARQUIVO_DADOS) -> dict:
    """
    Carrega os dados das máquinas a partir do arquivo JSON.
    Se o arquivo não existir ou estiver corrompido, inicializa uma estrutura padrão segura.
    """
    if not os.path.exists(caminho_arquivo):
        dados = {
            "maquinas": []
        }
        salvar_dados(dados, caminho_arquivo)
        return dados
    
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[AVISO] Arquivo {caminho_arquivo} corrompido ou inválido ({e}).")
        # Cria backup do arquivo com problema para não perder dados permanentemente
        backup_path = f"{caminho_arquivo}.corrompido.bak"
        try:
            shutil.copy(caminho_arquivo, backup_path)
            print(f"[AVISO] Backup criado em: {backup_path}")
        except Exception:
            pass
        dados = {"maquinas": []}
        salvar_dados(dados, caminho_arquivo)
        return dados


def salvar_dados(dados: dict, caminho_arquivo: str = ARQUIVO_DADOS) -> None:
    """
    Salva os dados de forma segura e atômica no arquivo JSON especificado.
    """
    arquivo_temp = f"{caminho_arquivo}.tmp"
    with open(arquivo_temp, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
    
    # Substitui atomicamente o arquivo principal
    os.replace(arquivo_temp, caminho_arquivo)
