'''analytics.py
Módulo de análise de dados e cálculo de health scores.
Implementa as funções usadas pelos testes e pelo main.
'''\n\nimport statistics\nfrom typing import List, Dict, Any\n\n\ndef calcular_estatisticas(historico: List[Dict[str, Any]], campo: str) -> Dict[str, float]:\n    """Calcula estatísticas básicas para um campo do histórico.
\n    Retorna um dicionário com média, mínimo, máximo, última leitura e desvio padrão.
    Se o histórico estiver vazio, todos os valores são 0.0.
    """\n    if not historico:\n        return {"media": 0.0, "min": 0.0, "max": 0.0, "ultima": 0.0, "desvio": 0.0}\n    valores = [item.get(campo, 0.0) for item in historico]\n    media = statistics.mean(valores)\n    minimo = min(valores)\n    maximo = max(valores)\n    ultima = valores[-1]\n    desvio = statistics.stdev(valores) if len(valores) > 1 else 0.0\n    return {"media": media, "min": minimo, "max": maximo, "ultima": ultima, "desvio": desvio}\n\n\ndef calcular_tendencia(historico: List[Dict[str, Any]], campo: str) -> str:\n    """Avalia a tendência de um campo.
\n    - Se houver menos de 2 pontos, retorna 'Estável'.\n    - Calcula a diferença entre a última e a primeira leitura.
    - Baseia‑se em thresholds simples para categorizar.
    """\n    if len(historico) < 2:
        return "Estável"
    primeira = historico[0].get(campo, 0.0)
    ultima = historico[-1].get(campo, 0.0)
    dif = ultima - primeira
    if dif > 15:
        return "Crescente Acelerada"
    if dif > 5:
        return "Leve Subida"
    if dif < -15:
        return "Decrescente Acelerada"
    if dif < -5:
        return "Queda Suave"
    return "Estável"
\n\ndef diagnosticar_causa_raiz(ultima: Dict[str, Any], baseline: Dict[str, Any]) -> List[str]:\n    """Gera hipóteses de causa raiz com base em desvios críticos.
\n    • Temperatura > 80 → possível falha mecânica grave.\n    • Vibração > 8 → desalinhamento ou desgaste.\n    • Consumo > 600 → sobrecarga elétrica.\n    """\n    hipoteses = []\n    if ultima.get('temperatura', 0) > 80:
        hipoteses.append('FALHA MECÂNICA GRAVE: temperatura muito alta')
    if ultima.get('vibracao', 0) > 8:
        hipoteses.append('DESALINHAMENTO: vibração acima do limite')
    if ultima.get('consumo', 0) > 600:
        hipoteses.append('SOBRECARGA ELÉTRICA: consumo fora do padrão')
    if not hipoteses:
        hipoteses.append('Nenhuma anomalia crítica detectada')
    return hipoteses\n\n\ndef _score_from_stats(stats: Dict[str, float]) -> float:\n    """Calcula um score simples a partir das estatísticas.
\n    Utiliza a média normalizada entre 0 e 100.
    """\n    # Supondo limites operacionais típicos\n    media = stats.get('media', 0.0)
    # Escala arbitrária: valores entre 0 e 120 são mapeados para 0‑100
    return max(0.0, min(100.0, 100 * (120 - media) / 120))\n\n\ndef calcular_indice_saude(historico: List[Dict[str, Any]]) -> Dict[str, Any]:\n    """Retorna um dicionário com score (0‑100) e classificação textual.
\n    A classificação segue a convenção usada nos testes:
    - >= 85 → Excelente\n    - >= 70 → Bom\n    - >= 50 → Médio\n    - < 50 → Crítico\n    """\n    if not historico:\n        return {"score": 0.0, "classificacao": "Sem Dados"}\n    stats = calcular_estatisticas(historico, 'temperatura')\n    score = _score_from_stats(stats)\n    if score >= 85:
        classificacao = 'Excelente'
    elif score >= 70:
        classificacao = 'Bom'
    elif score >= 50:
        classificacao = 'Médio'
    else:
        classificacao = 'Crítico'
    return {"score": round(score, 2), "classificacao": classificacao}\n