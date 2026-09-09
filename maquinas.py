from dados import salvar_dados

def cadastrar_maquina(dados):
    while True:
        IDs = []

        nome_da_maquina = input("    Digite o nome da maquina: ")
        status_da_maquina = input("    Qual o atual status da maquina (NORMAL/ATENÇÃO/ANOMALIA) : ")
    
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
        