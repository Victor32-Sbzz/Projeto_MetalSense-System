"""simulador_iot.py
Módulo simplificado que fornece cenários de telemetria e simulação contínua.
"""
import time
import itertools
from datetime import datetime
from typing import Dict, Any
from dados import carregar_dados, salvar_dados
from maquinas import registrar_leitura

# Definição de alguns cenários de teste
CENARIOS = {
    "normal": "Leitura padrão dentro da faixa operacional",
    "temperatura_alta": "Temperatura acima do limite",
    "vibracao_alta": "Vibração excessiva",
    "consumo_alto": "Consumo elétrico elevado",
    "mistura": "Múltiplas anomalias simultâneas",
}

def gerar_leitura_cenario(cenario: str, ciclo: int = 1) -> Dict[str, Any]:
    """Gera uma leitura única para o *cenario* especificado.
    O parâmetro *ciclo* permite variar os valores em chamadas sucessivas.
    """
    base = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # valores base normais
    temperatura = 60.0
    vibracao = 3.0
    consumo = 300.0
    if cenario == "temperatura_alta":
        temperatura += 30 + ciclo * 2
    elif cenario == "vibracao_alta":
        vibracao += 6 + ciclo
    elif cenario == "consumo_alto":
        consumo += 400 + ciclo * 10
    elif cenario == "mistura":
        temperatura += 25
        vibracao += 5
        consumo += 250
    # caso "normal" ou desconhecido, mantém valores padrão
    return {
        "timestamp": base,
        "temperatura": round(temperatura, 2),
        "vibracao": round(vibracao, 2),
        "consumo": round(consumo, 2),
    }

def executar_simulacao_continua(id_maquina: int, cenario: str = "normal", intervalo: float = 1.0, max_ciclos: int = 5) -> None:
    """Executa uma simulação simples, registrando *max_ciclos* leituras.
    Cada ciclo aguarda *intervalo* segundos. Esta implementação é síncrona
    e bloqueante, suficiente para os propósitos de teste.
    """
    dados = carregar_dados()
    for ciclo in range(1, max_ciclos + 1):
        leitura = gerar_leitura_cenario(cenario, ciclo)
        registrar_leitura(dados, id_maquina, leitura=leitura, gerar_anomalia=False)
        # Pequena pausa para imitar tempo real (não essencial em testes)
        time.sleep(intervalo)
