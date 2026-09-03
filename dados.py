import json
import os

ARQUIVO_DADOS = "dados.json"

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        dados = {
            "maquinas": []
        }

        salvar_dados(dados)
        return dados
    
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)
    

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
