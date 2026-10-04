"""
Módulo de Inteligência Analítica e Manutenção Preditiva do MetalSense.
Calcula o Health Score (Índice de Saúde), tendências de degradação temporal,
estimativa de risco de falha e diagnóstico de causa-raiz para máquinas industriais.
"""

import math
import statistics
from typing import Dict, List, Any


def calcular_estatisticas(historico: List[Dict[str, Any]], metrica: str) -> Dict[str, float]:
    """Calcula estatísticas descritivas completas para uma dada métrica."""
    if not historico:
        return {"min": 0.0, "max": 0.0, "media": 0.0, "desvio": 0.0, "ultima": 0.0}

    valores = [item[metrica] for item in historico if metrica in item]
    if not valores:
        return {"min": 0.0, "max": 0.0, "media": 0.0, "desvio": 0.0, "ultima": 0.0}

    media = statistics.mean(valores)
    desvio = statistics.stdev(valores) if len(valores) > 1 else 0.0
    return {
        "min": round(min(valores), 2),
        "max": round(max(valores), 2),
        "media": round(media, 2),
        "desvio": round(desvio, 2),
        "ultima": round(valores[-1], 2)
    }


def calcular_tendencia(historico: List[Dict[str, Any]], metrica: str, janela: int = 5) -> str:
    """
    Avalia a inclinação/taxa de variação (derivada discreta) nos últimos N pontos.
    Identifica aquecimento acelerado ou aumento progressivo de vibração.
    """
    if len(historico) < 3:
        return "Insuficiente"

    sub_historico = historico[-janela:]
    valores = [item[metrica] for item in sub_historico if metrica in item]
    if len(valores) < 3:
        return "Estável"

    # Regressão linear simples para encontrar a inclinação (slope)
    n = len(valores)
    x = list(range(n))
    media_x = sum(x) / n
    media_y = sum(valores) / n

    numerador = sum((x[i] - media_x) * (valores[i] - media_y) for i in range(n))
    denominador = sum((x[i] - media_x) ** 2 for i in range(n))

    if denominador == 0:
        return "Estável"

    inclinacao = numerador / denominador

    # Limiares de variação por ciclo
    limiares = {
        "temperatura": 0.8,   # >= 0.8°C por leitura indica aquecimento rápido
        "vibracao": 0.3,      # >= 0.3 mm/s por leitura indica desestabilização
        "consumo": 15.0       # >= 15 W por leitura indica esforço crescente
    }
    limiar = limiares.get(metrica, 0.5)

    if inclinacao > limiar:
        return "Crescente Acelerada"
    elif inclinacao > (limiar / 3):
        return "Leve Subida"
    elif inclinacao < -limiar:
        return "Queda Acelerada"
    elif inclinacao < -(limiar / 3):
        return "Leve Descida"
    else:
        return "Estável"


def diagnosticar_causa_raiz(ultima: Dict[str, Any], medias: Dict[str, float]) -> List[str]:
    """
    Identifica hipóteses mecânicas e elétricas de falha com base na correlação
    entre temperatura, vibração e consumo.
    """
    hipoteses = []
    temp = ultima.get("temperatura", 0.0)
    vib = ultima.get("vibracao", 0.0)
    pot = ultima.get("consumo", 0.0)

    # 1. Falha em Rolamentos / Mancais
    if vib > 7.0 and temp > 75.0:
        hipoteses.append("FALHA MECÂNICA GRAVE: Forte indício de desgaste severo de rolamento ou perda de lubrificação.")
    elif vib > 6.0 and temp <= 75.0:
        hipoteses.append("DESALINHAMENTO / DESBALANCEAMENTO: Vibração elevada com temperatura normal sugere folga mecânica ou desbalanceamento de eixo.")

    # 2. Sobrecarga de Motor / Atrito
    if pot > 480.0 and temp > 80.0:
        hipoteses.append("SOBRECARGA ELÉTRICA / TÉRMICA: Motor operando sob esforço crítico, risco de queima de enrolamento.")
    elif pot > 480.0 and temp <= 80.0:
        hipoteses.append("SOBRECARGA OPERACIONAL: Demanda mecânica elevada no processo produtivo.")

    # 3. Superaquecimento Isolado
    if temp > 85.0 and vib <= 6.0 and pot <= 480.0:
        hipoteses.append("FALHA DE REFRIGERAÇÃO: Superaquecimento sem aumento de esforço mecânico (checar ventoinha ou líquido de arrefecimento).")

    return hipoteses


def calcular_indice_saude(historico: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula o Health Score (Índice de Saúde) global de 0% a 100%.
    Combina desvios de temperatura, vibração, consumo e tendências temporais.
    """
    if not historico:
        return {
            "score": 100.0,
            "status": "sem dados",
            "classificacao": "Aguardando Telemetria",
            "cor": "#6c757d",
            "tendencias": {"temperatura": "Indefinida", "vibracao": "Indefinida", "consumo": "Indefinida"},
            "hipoteses": [],
            "recomendacao": "Inicie o registro de telemetria da máquina para ativar os algoritmos preditivos."
        }

    ultima = historico[-1]
    stats_temp = calcular_estatisticas(historico, "temperatura")
    stats_vib = calcular_estatisticas(historico, "vibracao")
    stats_pot = calcular_estatisticas(historico, "consumo")

    # Pontuação inicial máxima
    score = 100.0

    # Penalização por Temperatura (Ideal: 50 a 68°C)
    t = ultima.get("temperatura", 60.0)
    if t > 90.0:
        score -= 40.0
    elif t > 80.0:
        score -= 25.0
    elif t > 72.0:
        score -= 10.0

    # Penalização por Vibração (Ideal: 1.5 a 4.5 mm/s)
    v = ultima.get("vibracao", 3.0)
    if v > 10.0:
        score -= 40.0
    elif v > 7.0:
        score -= 25.0
    elif v > 5.0:
        score -= 10.0

    # Penalização por Consumo (Ideal: 200 a 400 W)
    p = ultima.get("consumo", 300.0)
    if p > 550.0:
        score -= 30.0
    elif p > 450.0:
        score -= 15.0

    # Tendências temporais
    tend_temp = calcular_tendencia(historico, "temperatura")
    tend_vib = calcular_tendencia(historico, "vibracao")
    tend_pot = calcular_tendencia(historico, "consumo")

    if tend_temp == "Crescente Acelerada":
        score -= 8.0
    if tend_vib == "Crescente Acelerada":
        score -= 10.0

    # Garantir limites [0, 100]
    score = max(0.0, min(100.0, round(score, 1)))

    # Classificação e Cores
    if score >= 85.0:
        classificacao = "Excelente (Operação Segura)"
        cor = "#28a745"
        recomendacao = "Equipamento em condições nominais de operação. Manter rotina de inspeção preventiva."
    elif score >= 70.0:
        classificacao = "Bom (Operação Normal)"
        cor = "#17a2b8"
        recomendacao = "Equipamento estável com pequenas oscilações normais de processo."
    elif score >= 50.0:
        classificacao = "Atenção (Degradação Detectada)"
        cor = "#ffc107"
        recomendacao = "Acompanhar tendências nas próximas 12 horas. Programar inspeção preventiva no próximo turno."
    else:
        classificacao = "Crítico (Risco Alto de Parada Não Planejada)"
        cor = "#dc3545"
        recomendacao = "INTERVENÇÃO IMEDIATA: Risco elevado de dano mecânico severo. Interromper máquina para manutenção."

    hipoteses = diagnosticar_causa_raiz(
        ultima,
        {"temperatura": stats_temp["media"], "vibracao": stats_vib["media"], "consumo": stats_pot["media"]}
    )

    return {
        "score": score,
        "classificacao": classificacao,
        "cor": cor,
        "estatisticas": {
            "temperatura": stats_temp,
            "vibracao": stats_vib,
            "consumo": stats_pot
        },
        "tendencias": {
            "temperatura": tend_temp,
            "vibracao": tend_vib,
            "consumo": tend_pot
        },
        "hipoteses": hipoteses,
        "recomendacao": recomendacao
    }
