from dados import salvar_dados
import random
import statistics


def criar_maquina (dados, nome_da_maquina):

    IDs = []

    for maquinas in dados["maquinas"]:
        IDs.append(maquinas['id'])

    if not IDs:
        id_nova_maquina = 1
    else:
        maior_id = max(IDs)
        id_nova_maquina = maior_id + 1

    nova_maquina = {
        'id' : id_nova_maquina,
        'nome' : nome_da_maquina,
        'status' : "sem dados",
        'historico' : []
    }
        
    dados["maquinas"].append(nova_maquina)
    salvar_dados(dados)

    return nova_maquina


def cadastrar_maquina(dados):
    while True:
        nome_da_maquina = input("    Digite o nome da maquina: ")
        maquina_criada = criar_maquina(dados, nome_da_maquina)
        
        print()
        escolha_menu_cadastro = input("    Deseja cadastrar mais alguma maquina? Digite sim (s) ou não (n): ")
        
        if escolha_menu_cadastro == "n":
            break
        elif escolha_menu_cadastro != "s":
            print("Informação incorreta!!! Tente novamente...")


def mostrar_maquinas(dados):
    while True:
        print("========================================")
        print("              METALSENSE")
        print("========================================")

        for maquina in dados["maquinas"]:
            print(f"    [ID {maquina['id']}] {maquina['nome']}")
            print(f"      Status: {maquina['status']}")
            print()
            
        sair_menu_maquinas = input("PARA SAIR DIGITE 'sair': ")
        if sair_menu_maquinas == "sair":
            break


def remover_maquina(dados, maquina_a_apagar):

    encontrou = False

    for maquina in dados["maquinas"]:
        if maquina_a_apagar == maquina['id']:
            encontrou = True        
            dados["maquinas"].remove(maquina)
            salvar_dados(dados)       
            break 

    return encontrou


def deletar_maquinas(dados):

    while True:
        for maquina in dados["maquinas"]:
            print(f"    [ID {maquina['id']}] {maquina['nome']}")
        
        maquina_a_apagar = int(input("Qual maquina deseja apagar? Digite o ID correspondente: "))
        encontrou = remover_maquina(dados, maquina_a_apagar)

        if encontrou == True:
            print("\n\nMaquina encontrada!!!")
            print("Maquina deletada com sucesso!!!\n\n")

        else:
            print("ID INCORRETO... maquina não encontrada!")
                    
        escolha_do_menu_deletar = input("Deletar mais alguma ou voltar ao menu? (digite: 'd'(deletar) ou 'v'(voltar)): ")
                
        if escolha_do_menu_deletar == "v":
            break
        elif escolha_do_menu_deletar != "d":
            print("Informação incorreta!!! Tente novamente...")


def simular_leitura():
    temperatura = round(random.uniform(40, 80), 2)
    vibracao = round(random.uniform(1, 10), 2)
    consumo = round(random.uniform(100, 500), 2)

    historico = {
        'temperatura' : temperatura,
        'vibracao' : vibracao,
        'consumo' : consumo
    }
    
    return historico


def analisar_maquina(dados, id_da_maquina):
    
    for maquina in dados["maquinas"]:
        if maquina['id'] == id_da_maquina:
            temperaturas = []
            for leitura in maquina['historico']:
                temperaturas.append(leitura['temperatura'])
            
            if len(temperaturas) < 2:
                return "Histórico insuficiente para análise."

            else:
                media = statistics.mean(temperaturas)
                desvio = statistics.stdev(temperaturas)
                ultima_leitura = temperaturas[-1]
                distancia = abs(ultima_leitura - media)
                limite = 2 * desvio

                if distancia > limite:
                    maquina['status'] = "anomalia"
                    salvar_dados(dados)
                    return "Possivel anomalia detectada...!"
                    
                else:
                    maquina['status'] = "normal"
                    salvar_dados(dados)
                    return "Comportamento dentro do padrão...!"

    return "ID não encontrado..."


def registrar_leitura(dados, id_da_maquina):
    for maquina in dados["maquinas"]:
        if maquina['id'] == id_da_maquina:
            leitura = simular_leitura()
            maquina['historico'].append(leitura)
            resultado_analise = analisar_maquina(dados, id_da_maquina)
            salvar_dados(dados)
            return resultado_analise

    return "ID não encontrado..."


def registrar_medicao(dados):
    id_da_maquina = int(input("    Digite o ID da máquina: "))
    resultado = registrar_leitura(dados, id_da_maquina)
    print(f"\n    {resultado}")