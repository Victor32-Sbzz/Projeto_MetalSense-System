from dados import salvar_dados
import random
import statistics



def cadastrar_maquina(dados):
    while True:
        IDs = []

        nome_da_maquina = input("    Digite o nome da maquina: ")
    
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
            'status' : "sem dados",
            'historico' : []
        }
    
        dados["maquinas"].append(nova_maquina)
        salvar_dados(dados)
        
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

       
def deletar_maquinas(dados):
    while True:
        for maquina in dados["maquinas"]:
            print(f"    [ID {maquina['id']}] {maquina['nome']}")
    
        maquina_a_apagar = int(input("Qual maquina deseja apagar? Digite o ID correspondente: "))
        
        encontrou = False
        
        for maquina in dados["maquinas"]:
            if maquina_a_apagar == maquina['id']:
                encontrou = True
                print("\n\nMaquina encontrada!!!")
                
                dados["maquinas"].remove(maquina)
                print("Maquina deletada com sucesso!!!\n\n")
                salvar_dados(dados)
                
                break 
            
        if encontrou == False:
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


def registrar_medicao(dados):
    id_da_maquina = int(input("    Digite o ID da máquina: "))
    
    encontrou = False
    
    for maquina in dados["maquinas"]:
        if maquina['id'] == id_da_maquina:
            encontrou = True
            leitura = simular_leitura()
            maquina['historico'].append(leitura)
            analisar_maquina(dados, id_da_maquina)
            print("\n    Historico adicionado com sucesso!!!")
            break
    
    if encontrou == False:
        print("ID INCORRETO... maquina não encontrada!")


def analisar_maquina(dados, id_da_maquina):
    
    for maquina in dados["maquinas"]:

        if maquina['id'] == id_da_maquina:

            temperaturas = []
            for leitura in maquina['historico']:
                temperaturas.append(leitura['temperatura'])
            
            if len(temperaturas) < 2:
                print("\n    Histórico insuficiente para análise.")

            else:
                media = statistics.mean(temperaturas)
                desvio = statistics.stdev(temperaturas)
                ultima_leitura = temperaturas[-1]
                distancia = abs(ultima_leitura - media)
                limite = 2 * desvio

                if distancia > limite:
                    print("\n    Possivel anomalia detectada...!")
                    maquina['status'] = "anomalia"
                    
                else:
                    print("\n    Comportamento dentro do padrão...!")
                    maquina['status'] = "normal"

                salvar_dados(dados)

            break