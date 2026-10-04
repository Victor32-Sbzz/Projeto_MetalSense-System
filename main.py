from dados import carregar_dados
from maquinas import (
    mostrar_maquinas,
    deletar_maquinas,
    cadastrar_maquina,
    registrar_medicao,
    consultar_analise,
)

def menu():
    print("\n========================================")
    print("              METALSENSE")
    print("========================================")
    print("  Escolha uma das seguintes opções:")
    print("  1 -- Cadastrar máquina")
    print("  2 -- Consultar máquinas cadastradas")
    print("  3 -- Registrar medição / telemetria")
    print("  4 -- Diagnosticar / analisar máquina")
    print("  5 -- Deletar máquina pelo ID")
    print("  6 -- Sair...")
    print("========================================")


def main():
    dados = carregar_dados()
    print("\nMetalSense iniciado com sucesso!")

    while True:
        menu()
        escolha_do_menu = input("Digite sua escolha: ").strip()

        if escolha_do_menu == '1':
            cadastrar_maquina(dados)

        elif escolha_do_menu == '2':
            mostrar_maquinas(dados)

        elif escolha_do_menu == '3':
            registrar_medicao(dados)

        elif escolha_do_menu == '4':
            consultar_analise(dados)

        elif escolha_do_menu == '5':
            deletar_maquinas(dados)

        elif escolha_do_menu == '6':
            print("\nEncerrando o MetalSense...")
            print("Até logo!\n")
            break

        else:
            print("\n[ERRO] Escolha inválida! Por favor, selecione uma das opções numéricas do menu.")


if __name__ == "__main__":
    main()