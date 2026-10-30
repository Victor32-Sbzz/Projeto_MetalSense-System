"""
Simulador de Sensores Industriais IoT para o MetalSense.
Permite injetar leituras em tempo real, gerar fluxos contínuos de telemetria
e simular falhas mecânicas com precisão física.
"""

import time
import random
import argparse
from datetime import datetime
from dados import carregar_dados, salvar_dados
from maquinas import registrar_leitura, simular_leitura


CENARIOS = {
    "normal": "Operação normal e estável de fábrica",
    "rolamento": "Desgaste progressivo de rolamento (vibração crescente)",
    "aquecimento": "Superaquecimento por falha de arrefecimento (temperatura crítica)",
    "sobrecarga": "Sobrecarga mecânica do processo (consumo elevado)"
}


def gerar_leitura_cenario(cenario: str, ciclo: int = 1) -> dict:
    """Gera uma leitura de telemetria baseada em um cenário físico específico."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if cenario == "rolamento":
        # Vibração sobe progressivamente com os ciclos
        vibracao = round(4.0 + (ciclo * 0.8) + random.uniform(-0.3, 0.5), 2)
        temperatura = round(62.0 + (ciclo * 0.4) + random.uniform(-1.0, 1.0), 2)
        consumo = round(320.0 + random.uniform(-15.0, 15.0), 2)

    elif cenario == "aquecimento":
        # Temperatura aumenta progressivamente
        temperatura = round(65.0 + (ciclo * 1.5) + random.uniform(-0.5, 0.8), 2)
        vibracao = round(3.2 + random.uniform(-0.2, 0.3), 2)
        consumo = round(310.0 + (ciclo * 5.0) + random.uniform(-10.0, 10.0), 2)

    elif cenario == "sobrecarga":
        # Consumo elétrico em pico
        consumo = round(520.0 + (ciclo * 12.0) + random.uniform(-20.0, 30.0), 2)
        temperatura = round(70.0 + (ciclo * 0.9) + random.uniform(-0.8, 1.2), 2)
        vibracao = round(5.5 + random.uniform(-0.5, 0.8), 2)

    else:
        # Padrão normal com ruído natural
        temperatura = round(random.gauss(60.0, 2.5), 2)
        vibracao = round(random.gauss(3.0, 0.4), 2)
        consumo = round(random.gauss(310.0, 18.0), 2)

    return {
        "timestamp": agora,
        "temperatura": max(20.0, temperatura),
        "vibracao": max(0.1, vibracao),
        "consumo": max(50.0, consumo)
    }


def executar_simulacao_continua(id_maquina: int, cenario: str = "normal", intervalo: float = 2.0, max_ciclos: int = 10) -> None:
    """Executa um fluxo contínuo de envio de dados para uma máquina."""
    dados = carregar_dados()
    maquina_alvo = None
    for m in dados.get("maquinas", []):
        if m["id"] == id_maquina:
            maquina_alvo = m
            break

    if not maquina_alvo:
        print(f"[ERRO] Máquina com ID {id_maquina} não encontrada!")
        return

    print(f"\n=======================================================")
    print(f"📡 INICIANDO GATEWAY IOT - MÁQUINA: {maquina_alvo['nome']} (ID {id_maquina})")
    print(f"⚙️ Cenário: {cenario.upper()} ({CENARIOS.get(cenario, '')})")
    print(f"⏱️ Intervalo: {intervalo}s | Total de ciclos: {max_ciclos}")
    print(f"=======================================================\n")

    for ciclo in range(1, max_ciclos + 1):
        leitura = gerar_leitura_cenario(cenario, ciclo=ciclo)
        resultado = registrar_leitura(dados, id_maquina, leitura=leitura)
        print(f"[{leitura['timestamp']}] Ciclo {ciclo}/{max_ciclos} -> "
              f"Temp: {leitura['temperatura']}°C | Vib: {leitura['vibracao']} mm/s | Consumo: {leitura['consumo']} W "
              f"-> Status: {resultado}")
        if ciclo < max_ciclos:
            time.sleep(intervalo)

    print("\n✅ Simulação finalizada com sucesso! Dados sincronizados no sistema.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de Sensores Industriais IoT - MetalSense")
    parser.add_argument("--id", type=int, default=1, help="ID da máquina de destino")
    parser.add_argument("--cenario", type=str, choices=list(CENARIOS.keys()), default="normal", help="Cenário de telemetria a ser simulado")
    parser.add_argument("--intervalo", type=float, default=1.5, help="Intervalo em segundos entre leituras")
    parser.add_argument("--ciclos", type=int, default=5, help="Quantidade de leituras a simular")

    args = parser.parse_args()
    executar_simulacao_continua(args.id, args.cenario, args.intervalo, args.ciclos)
