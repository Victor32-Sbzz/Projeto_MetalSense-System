from dados import salvar_dados
import random
import statistics
from datetime import datetime


def criar_maquina(dados: dict, nome_da_maquina: str) -> dict:
    """
    Função de lógica pura: cria e cadastra uma nova máquina no dicionário de dados.
    Lança ValueError se o nome for vazio ou contiver apenas espaços.
    """
    nome_limpo = nome_da_maquina.strip()
    if not nome_limpo:
        raise ValueError("O nome da máquina não pode ser vazio.")

    ids = [m['id'] for m in dados.get("maquinas", []) if isinstance(m.get('id'), int)]
    id_nova_maquina = max(ids) + 1 if ids else 1

    nova_maquina = {
        'id': id_nova_maquina,
        'nome': nome_limpo,
        'status': "sem dados",
        'historico': []
    }

    if "maquinas" not in dados:
        dados["maquinas"] = []

    dados["maquinas"].append(nova_maquina)
    salvar_dados(dados)

    return nova_maquina


def remover_maquina(dados: dict, id_maquina: int) -> bool:
    """
    Função de lógica pura: remove a máquina com o ID fornecido.
    Retorna True se encontrou e removeu, False caso contrário.
    """
    for maquina in dados.get("maquinas", []):
        if maquina.get('id') == id_maquina:
            dados["maquinas"].remove(maquina)
            salvar_dados(dados)
            return True
    return False


def simular_leitura(gerar_anomalia: bool = False) -> dict:
    """
    Função de lógica pura: simula uma leitura de telemetria industrial com timestamp.
    Se gerar_anomalia for True, gera picos fora do padrão operacional.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not gerar_anomalia:
        # Padrão operacional normal
        temperatura = round(random.uniform(55.0, 68.0), 2)
        vibracao = round(random.uniform(2.0, 4.5), 2)
        consumo = round(random.uniform(250.0, 380.0), 2)
    else:
        # Padrão anômalo (picos críticos)
        tipo = random.choice(["temperatura", "vibracao", "consumo", "multiplo"])
        if tipo == "temperatura":
            temperatura = round(random.uniform(88.0, 115.0), 2)
            vibracao = round(random.uniform(2.0, 4.5), 2)
            consumo = round(random.uniform(250.0, 380.0), 2)
        elif tipo == "vibracao":
            temperatura = round(random.uniform(55.0, 68.0), 2)
            vibracao = round(random.uniform(9.5, 18.0), 2)
            consumo = round(random.uniform(250.0, 380.0), 2)
        elif tipo == "consumo":
            temperatura = round(random.uniform(55.0, 68.0), 2)
            vibracao = round(random.uniform(2.0, 4.5), 2)
            consumo = round(random.uniform(550.0, 850.0), 2)
        else:
            temperatura = round(random.uniform(85.0, 110.0), 2)
            vibracao = round(random.uniform(10.0, 16.0), 2)
            consumo = round(random.uniform(500.0, 750.0), 2)

    return {
        'timestamp': agora,
        'temperatura': temperatura,
        'vibracao': vibracao,
        'consumo': consumo
    }


def analisar_maquina(dados: dict, id_da_maquina: int) -> str:
    """
    Função de lógica pura: avalia o histórico da máquina buscando anomalias
    em temperatura, vibração e consumo (desvio padrão e limites críticos).
    """
    for maquina in dados.get("maquinas", []):
        if maquina.get('id') == id_da_maquina:
            historico = maquina.get('historico', [])
            if len(historico) < 2:
                maquina['status'] = "sem dados"
                salvar_dados(dados)
                return "Histórico insuficiente para análise (mínimo de 2 medições necessárias)."

            ultima = historico[-1]
            motivos_anomalia = []

            # 1. Checagem por limites críticos absolutos
            if ultima['temperatura'] > 85.0:
                motivos_anomalia.append(f"Temperatura crítica ({ultima['temperatura']}°C)")
            if ultima['vibracao'] > 8.0:
                motivos_anomalia.append(f"Vibração excessiva ({ultima['vibracao']} mm/s)")
            if ultima['consumo'] > 500.0:
                motivos_anomalia.append(f"Consumo elétrico anormal ({ultima['consumo']} W)")

            # 2. Checagem estatística em relação ao histórico próprio
            if not motivos_anomalia and len(historico) >= 3:
                # Usa histórico anterior como baseline
                leituras_base = historico[:-1]
                for metrica, nome_metrica, unidade in [
                    ('temperatura', 'Temperatura', '°C'),
                    ('vibracao', 'Vibração', 'mm/s'),
                    ('consumo', 'Consumo', 'W')
                ]:
                    valores = [item[metrica] for item in leituras_base]
                    media = statistics.mean(valores)
                    desvio = statistics.stdev(valores) if len(valores) > 1 else 0.0

                    if desvio > 0.05:  # Evita falsos positivos com variações mínimas
                        distancia = abs(ultima[metrica] - media)
                        if distancia > (2.5 * desvio):
                            motivos_anomalia.append(
                                f"{nome_metrica} fora do padrão histórico ({ultima[metrica]} {unidade} vs média {media:.2f} {unidade})"
                            )

            if motivos_anomalia:
                maquina['status'] = "anomalia"
                salvar_dados(dados)
                return f"Possível anomalia detectada: {', '.join(motivos_anomalia)}!"
            else:
                maquina['status'] = "normal"
                salvar_dados(dados)
                return "Comportamento dentro do padrão operacional normal!"

    return "ID não encontrado..."


def registrar_leitura(dados: dict, id_da_maquina: int, leitura: dict = None, gerar_anomalia: bool = False) -> str:
    """
    Função de lógica pura: registra uma nova leitura para a máquina especificada
    e dispara a análise automática.
    """
    for maquina in dados.get("maquinas", []):
        if maquina.get('id') == id_da_maquina:
            if leitura is None:
                leitura = simular_leitura(gerar_anomalia=gerar_anomalia)
            
            if 'timestamp' not in leitura:
                leitura['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            maquina.setdefault('historico', []).append(leitura)
            resultado_analise = analisar_maquina(dados, id_da_maquina)
            return resultado_analise

    return "ID não encontrado..."


# ==============================================================================
# FUNÇÕES DE INTERAÇÃO (CLI)
# ==============================================================================

def cadastrar_maquina(dados: dict) -> None:
    """Interação CLI para cadastro de máquinas."""
    while True:
        nome_da_maquina = input("\n    Digite o nome da máquina: ").strip()
        if not nome_da_maquina:
            print("    [ERRO] O nome da máquina não pode ser vazio. Tente novamente.")
            continue

        maquina_criada = criar_maquina(dados, nome_da_maquina)
        print(f"    Máquina cadastrada com sucesso! [ID {maquina_criada['id']}] {maquina_criada['nome']}")

        escolha = input("\n    Deseja cadastrar mais alguma máquina? (s/n): ").strip().lower()
        if escolha == "n":
            break
        elif escolha != "s":
            print("    Opção inválida, voltando ao menu.")
            break


def mostrar_maquinas(dados: dict) -> None:
    """Interação CLI para consulta de máquinas e status."""
    print("\n========================================")
    print("        MÁQUINAS CADASTRADAS")
    print("========================================")

    maquinas = dados.get("maquinas", [])
    if not maquinas:
        print("    Nenhuma máquina cadastrada no momento.\n")
        input("Pressione Enter para voltar ao menu...")
        return

    for maquina in maquinas:
        status = maquina.get('status', 'sem dados').upper()
        print(f"\n    [ID {maquina['id']}] {maquina['nome']}")
        print(f"      Status: {status}")
        historico = maquina.get('historico', [])
        print(f"      Total de medições: {len(historico)}")
        if historico:
            ultima = historico[-1]
            data = ultima.get('timestamp', 'Sem data')
            print(f"      Última leitura ({data}):")
            print(f"        - Temp: {ultima['temperatura']} °C")
            print(f"        - Vibração: {ultima['vibracao']} mm/s")
            print(f"        - Consumo: {ultima['consumo']} W")

    print("\n" + "=" * 40)
    input("Pressione Enter para voltar ao menu...")


def deletar_maquinas(dados: dict) -> None:
    """Interação CLI para exclusão de máquinas."""
    while True:
        maquinas = dados.get("maquinas", [])
        if not maquinas:
            print("\n    Nenhuma máquina cadastrada para deletar.")
            break

        print("\nMáquinas disponíveis:")
        for maquina in maquinas:
            print(f"    [ID {maquina['id']}] {maquina['nome']}")

        entrada_id = input("\nQual máquina deseja apagar? Digite o ID (ou 'v' para voltar): ").strip()
        if entrada_id.lower() == 'v':
            break

        try:
            id_para_apagar = int(entrada_id)
        except ValueError:
            print("    [ERRO] Por favor, digite um número de ID válido.")
            continue

        if remover_maquina(dados, id_para_apagar):
            print(f"\n    Máquina ID {id_para_apagar} removida com sucesso!")
        else:
            print(f"\n    [ERRO] Máquina com ID {id_para_apagar} não encontrada.")

        escolha = input("\nDeletar mais alguma máquina? (d: deletar / v: voltar): ").strip().lower()
        if escolha == "v":
            break


def registrar_medicao(dados: dict) -> None:
    """Interação CLI para registrar telemetria (normal ou simulando anomalia)."""
    maquinas = dados.get("maquinas", [])
    if not maquinas:
        print("\n    Nenhuma máquina cadastrada. Cadastre uma máquina primeiro.")
        return

    print("\nMáquinas cadastradas:")
    for maquina in maquinas:
        print(f"    [ID {maquina['id']}] {maquina['nome']}")

    entrada_id = input("\n    Digite o ID da máquina: ").strip()
    try:
        id_da_maquina = int(entrada_id)
    except ValueError:
        print("    [ERRO] ID inválido. Digite um número inteiro.")
        return

    print("    Tipo de medição:")
    print("    1 - Simular leitura operacional normal")
    print("    2 - Simular falha/anomalia (teste de detecção)")
    opcao = input("    Escolha (1 ou 2): ").strip()

    gerar_anomalia = (opcao == '2')
    resultado = registrar_leitura(dados, id_da_maquina, gerar_anomalia=gerar_anomalia)
    print(f"\n    Resultado: {resultado}")


def consultar_analise(dados: dict) -> None:
    """Interação CLI para analisar o comportamento atual de uma máquina sob demanda."""
    maquinas = dados.get("maquinas", [])
    if not maquinas:
        print("\n    Nenhuma máquina cadastrada.")
        return

    print("\nMáquinas cadastradas:")
    for maquina in maquinas:
        print(f"    [ID {maquina['id']}] {maquina['nome']} - Status: {maquina.get('status', 'sem dados')}")

    entrada_id = input("\n    Digite o ID da máquina para consultar análise detalhada: ").strip()
    try:
        id_da_maquina = int(entrada_id)
    except ValueError:
        print("    [ERRO] ID inválido. Digite um número inteiro.")
        return

    resultado = analisar_maquina(dados, id_da_maquina)
    print(f"\n    Diagnóstico: {resultado}")