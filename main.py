import sys
from dados import carregar_dados
from maquinas import (
    mostrar_maquinas,
    deletar_maquinas,
    cadastrar_maquina,
    registrar_medicao,
    consultar_analise,
)
from analytics import calcular_indice_saude
from relatorios import gerar_ordem_servico_texto, exportar_historico_csv, gerar_relatorio_html
from simulador_iot import executar_simulacao_continua, CENARIOS


# Cores ANSI para terminais modernos
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"


def banner():
    print(f"""{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════╗
║   ⚙️   M E T A L S E N S E   -   S Y S T E M   P R O   v 2 . 0   ║
║      Inteligência Preditiva Industrial & Monitoramento IoT       ║
║                       TechForge Team                             ║
╚══════════════════════════════════════════════════════════════════╝{RESET}""")


def menu_principal():
    print(f"\n{BOLD}PAINEL DE CONTROLE INDUSTRIAL:{RESET}")
    print(f"  {CYAN}1{RESET} -- Cadastrar nova máquina")
    print(f"  {CYAN}2{RESET} -- Consultar máquinas & Health Scores")
    print(f"  {CYAN}3{RESET} -- Registrar telemetria (manual ou simulação pontual)")
    print(f"  {CYAN}4{RESET} -- Diagnóstico Preditivo Avançado (Causa-Raiz)")
    print(f"  {CYAN}5{RESET} -- Gerar Relatório Técnico / Ordem de Serviço (OS)")
    print(f"  {CYAN}6{RESET} -- Simulador de Fluxo Contínuo IoT (Injeção de Falhas)")
    print(f"  {CYAN}7{RESET} -- Deletar máquina pelo ID")
    print(f"  {RED}8{RESET} -- Sair do sistema")
    print(f"{GRAY}──────────────────────────────────────────────────────────────────{RESET}")


def listar_com_saude(dados: dict):
    """Exibe um painel visual consolidado com Health Scores e status coloridos."""
    maquinas = dados.get("maquinas", [])
    if not maquinas:
        print(f"\n{YELLOW}Nenhuma máquina cadastrada no momento.{RESET}")
        return

    print(f"\n{BOLD}{'ID':<4} | {'NOME DA MÁQUINA':<24} | {'STATUS':<12} | {'HEALTH SCORE':<16} | {'LEITURAS'}{RESET}")
    print("─" * 70)
    for m in maquinas:
        historico = m.get("historico", [])
        saude = calcular_indice_saude(historico)
        score = saude["score"]

        # Colorização condicional
        if score >= 85:
            cor_score = f"{GREEN}{score:>5.1f}%{RESET}"
        elif score >= 60:
            cor_score = f"{YELLOW}{score:>5.1f}%{RESET}"
        else:
            cor_score = f"{RED}{score:>5.1f}%{RESET}"

        status_txt = m.get("status", "sem dados").upper()
        if "ANOMALIA" in status_txt:
            status_cor = f"{RED}{status_txt:<12}{RESET}"
        elif "NORMAL" in status_txt:
            status_cor = f"{GREEN}{status_txt:<12}{RESET}"
        else:
            status_cor = f"{GRAY}{status_txt:<12}{RESET}"

        print(f"{m['id']:<4} | {m['nome'][:24]:<24} | {status_cor} | {cor_score:<24} | {len(historico)}")
    print("─" * 70)


def submenu_relatorios(dados: dict):
    """Menu para emissão de laudos e exportação de dados."""
    listar_com_saude(dados)
    entrada = input("\nDigite o ID da máquina para gerar relatório (ou 'v' para voltar): ").strip()
    if entrada.lower() == 'v':
        return

    try:
        id_m = int(entrada)
    except ValueError:
        print(f"{RED}[ERRO] ID inválido.{RESET}")
        return

    maquina = next((m for m in dados.get("maquinas", []) if m["id"] == id_m), None)
    if not maquina:
        print(f"{RED}[ERRO] Máquina não encontrada.{RESET}")
        return

    print("\nOpções de Relatório:")
    print("1 - Visualizar Ordem de Serviço (OS) no Terminal")
    print("2 - Exportar Histórico para Planilha CSV")
    print("3 - Gerar Laudo Técnico em HTML (Para Impressão/Auditoria)")
    esc = input("Escolha uma opção: ").strip()

    if esc == '1':
        print("\n" + gerar_ordem_servico_texto(maquina))
    elif esc == '2':
        arq = exportar_historico_csv(maquina)
        print(f"{GREEN}✅ Arquivo exportado com sucesso: {arq}{RESET}")
    elif esc == '3':
        arq = gerar_relatorio_html(maquina)
        print(f"{GREEN}✅ Laudo HTML gerado: {arq} (abra no navegador){RESET}")


def submenu_iot(dados: dict):
    """Submenu para disparar simulações contínuas de sensores IoT."""
    listar_com_saude(dados)
    entrada = input("\nDigite o ID da máquina de destino para o fluxo IoT (ou 'v' para voltar): ").strip()
    if entrada.lower() == 'v':
        return

    try:
        id_m = int(entrada)
    except ValueError:
        print(f"{RED}[ERRO] ID inválido.{RESET}")
        return

    print("\nCenários de Telemetria Disponíveis:")
    for k, v in CENARIOS.items():
        print(f"  • {BOLD}{k:<12}{RESET} -> {v}")

    cenario = input("Digite o nome do cenário (padrão: normal): ").strip().lower()
    if cenario not in CENARIOS:
        cenario = "normal"

    try:
        ciclos = int(input("Quantidade de ciclos/leituras (padrão: 5): ") or 5)
    except ValueError:
        ciclos = 5

    executar_simulacao_continua(id_m, cenario=cenario, intervalo=1.0, max_ciclos=ciclos)


def main():
    dados = carregar_dados()
    banner()

    while True:
        menu_principal()
        escolha = input(f"{BOLD}Digite sua escolha (1-8): {RESET}").strip()

        if escolha == '1':
            cadastrar_maquina(dados)

        elif escolha == '2':
            listar_com_saude(dados)
            mostrar_maquinas(dados)

        elif escolha == '3':
            registrar_medicao(dados)

        elif escolha == '4':
            listar_com_saude(dados)
            consultar_analise(dados)

        elif escolha == '5':
            submenu_relatorios(dados)

        elif escolha == '6':
            submenu_iot(dados)

        elif escolha == '7':
            deletar_maquinas(dados)

        elif escolha == '8':
            print(f"\n{CYAN}Encerrando o MetalSense System Pro...{RESET}")
            print(f"{GREEN}TechForge: Transformando dados industriais em inteligência preditiva. Até logo!{RESET}\n")
            break

        else:
            print(f"{RED}[ERRO] Opção inválida! Escolha um número de 1 a 8.{RESET}")


if __name__ == "__main__":
    main()