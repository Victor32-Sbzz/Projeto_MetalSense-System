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

def cadastrar_maquina():

    IDs = []

    nome_da_maquina = input("Digite o nome da maquina: ")
    status_da_maquina = input("Qual o atual status da maquina (NORMAL/ATENÇÃO/ANOMALIA) : ")
    
    for maquinas in dados["maquinas"]:
        IDs.append(maquinas['id'])
    
    if not IDs:
        id_nova_maquina = 1
    else:
        maior_id = max(IDs)
        id_nova_maquina =  maior_id + 1

    nova_maquina = {
        'id' : id_nova_maquina,
        'nome' : nome_da_maquina,
        'status' : status_da_maquina,
        'historico' : []
    }
    
    dados["maquinas"].append(nova_maquina)
    salvar_dados(dados)

dados = carregar_dados()

print("MetalSense iniciado com sucesso!")
cadastrar_maquina()
print(dados)
