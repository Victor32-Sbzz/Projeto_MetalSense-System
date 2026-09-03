from dados import carregar_dados, salvar_dados

def menu():
    print("========================================")
    print("              METALSENSE")
    print("========================================")
    print("\n  Escolha uma das seguintes opções:")
    print("\n1 -- Cadastrar maquina\n2 -- Consultar maquinas cadastradas\n3 -- Deletar maquina pelo ID\n4 -- Sair...\n")

def cadastrar_maquina():
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
            
def mostrar_maquinas():
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
        
def deletar_maquinas():
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
        
dados = carregar_dados()

print
print("MetalSense iniciado com sucesso!")
print()
while True:
    menu()
    escolha_do_menu = input("Digite sua escolha: ")

    if escolha_do_menu == '1':
        print("  Entrando no modulo de cadastro...")
        cadastrar_maquina()

    elif escolha_do_menu == '2':
        print("  Entrando no modulo de consulta...")
        mostrar_maquinas()

    elif escolha_do_menu == '3':
        print("  Entrando no modulo de remoção...")
        deletar_maquinas()

    elif escolha_do_menu == '4':
        print("\n\n     parando o metalsense...")
        print("     TCHAUU\n\n")
        break

    else:
        print("ESCOLHA INVALIDA!!! Por favor, escolha uma das opções disponiveis.")