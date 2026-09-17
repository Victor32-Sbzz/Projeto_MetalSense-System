from dados import carregar_dados
from maquinas import mostrar_maquinas, deletar_maquinas, cadastrar_maquina, registrar_medicao, analisar_maquina

def menu():
    print("========================================")
    print("              METALSENSE")
    print("========================================")
    print("\n  Escolha uma das seguintes opções:")
    print("\n1 -- Cadastrar maquina\n2 -- Consultar maquinas cadastradas\n3 -- Registrar medição\n4 -- Deletar maquina pelo ID\n5 -- Sair...\n")

dados = carregar_dados()

print
print("MetalSense iniciado com sucesso!")
print()
while True:
    menu()
    escolha_do_menu = input("Digite sua escolha: ")

    if escolha_do_menu == '1':
        print("  Entrando no modulo de cadastro...")
        cadastrar_maquina(dados)

    elif escolha_do_menu == '2':
        print("  Entrando no modulo de consulta...")
        mostrar_maquinas(dados)

    elif escolha_do_menu == '3':
        print("  Entrando no modulo de registrar medição...")
        registrar_medicao(dados)

    elif escolha_do_menu == '4':
        print("  Entrando no modulo de deletar maquinas...")
        deletar_maquinas(dados)

    elif escolha_do_menu == '5':
        print("\n\n     parando o metalsense...")
        print("     TCHAUU\n\n")
        break

    else:
        print("ESCOLHA INVALIDA!!! Por favor, escolha uma das opções disponiveis.")