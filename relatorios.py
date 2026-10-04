"""
Módulo de Geração de Relatórios e Auditoria Preditiva do MetalSense.
Exporta telemetria para CSV e gera laudos técnicos de manutenção em HTML e Markdown.
"""

import os
import csv
from datetime import datetime
from analytics import calcular_indice_saude


def exportar_historico_csv(maquina: dict, caminho_destino: str = None) -> str:
    """Exporta todo o histórico de telemetria de uma máquina para arquivo CSV."""
    if not caminho_destino:
        caminho_destino = f"relatorio_maquina_{maquina['id']}.csv"

    historico = maquina.get("historico", [])
    if not historico:
        return ""

    campos = ["timestamp", "temperatura", "vibracao", "consumo"]
    with open(caminho_destino, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for linha in historico:
            writer.writerow({
                "timestamp": linha.get("timestamp", ""),
                "temperatura": linha.get("temperatura", 0.0),
                "vibracao": linha.get("vibracao", 0.0),
                "consumo": linha.get("consumo", 0.0)
            })

    return caminho_destino


def gerar_ordem_servico_texto(maquina: dict) -> str:
    """Gera uma Ordem de Serviço (OS) técnica em formato texto para console ou ticket."""
    historico = maquina.get("historico", [])
    saude = calcular_indice_saude(historico)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    linhas = [
        "=" * 60,
        "          ORDEM DE SERVIÇO DE MANUTENÇÃO PREDITIVA",
        "                      SISTEMA METALSENSE",
        "=" * 60,
        f"Data de Emissão: {agora}",
        f"Identificação:   [ID {maquina['id']}] {maquina['nome']}",
        f"Status Atual:    {maquina.get('status', 'sem dados').upper()}",
        f"Health Score:    {saude['score']}% ({saude['classificacao']})",
        "-" * 60,
        "DIAGNÓSTICO TÉCNICO E TENDÊNCIAS:",
        f"  • Temperatura:  Tendência {saude['tendencias']['temperatura']}",
        f"  • Vibração:     Tendência {saude['tendencias']['vibracao']}",
        f"  • Consumo:      Tendência {saude['tendencias']['consumo']}",
        "-" * 60,
        "HIPÓTESES MECÂNICAS IDENTIFICADAS:"
    ]

    if saude["hipoteses"]:
        for h in saude["hipoteses"]:
            linhas.append(f"  [ALERTA] {h}")
    else:
        linhas.append("  Nenhum padrão crítico de falha iminente identificado.")

    linhas.extend([
        "-" * 60,
        "RECOMENDAÇÃO OPERACIONAL:",
        f"  {saude['recomendacao']}",
        "=" * 60
    ])

    return "\n".join(linhas)


def gerar_relatorio_html(maquina: dict, caminho_arquivo: str = None) -> str:
    """Gera um laudo de auditoria preditiva estilisado em HTML pronto para impressão."""
    if not caminho_arquivo:
        caminho_arquivo = f"relatorio_maquina_{maquina['id']}.html"

    historico = maquina.get("historico", [])
    saude = calcular_indice_saude(historico)
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    linhas_tabela = ""
    for item in reversed(historico[-15:]):
        linhas_tabela += f"""
        <tr>
            <td>{item.get('timestamp', '-')}</td>
            <td>{item.get('temperatura', '-')} °C</td>
            <td>{item.get('vibracao', '-')} mm/s</td>
            <td>{item.get('consumo', '-')} W</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Laudo Técnico - {maquina['nome']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); max-width: 900px; margin: auto; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #334155; padding-bottom: 15px; }}
        .badge {{ padding: 6px 14px; border-radius: 20px; font-weight: bold; background: {saude['cor']}; color: white; display: inline-block; }}
        .score {{ font-size: 32px; font-weight: bold; color: {saude['cor']}; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; }}
        .alert {{ background: #450a0a; border-left: 4px solid #ef4444; padding: 12px; margin-top: 15px; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div>
                <h1>⚙️ MetalSense - Laudo Técnico</h1>
                <p>Relatório de Manutenção Preditiva & Inteligência Industrial</p>
            </div>
            <div style="text-align: right;">
                <span class="badge">{saude['classificacao']}</span>
                <div class="score">{saude['score']}%</div>
            </div>
        </div>
        <p><strong>Equipamento:</strong> [ID {maquina['id']}] {maquina['nome']} | <strong>Emissão:</strong> {agora}</p>
        
        <h3>Diagnóstico Preditivo</h3>
        <p>{saude['recomendacao']}</p>
        
        {f'<div class="alert"><strong>Alertas Mecânicos:</strong><br>' + '<br>'.join(saude['hipoteses']) + '</div>' if saude['hipoteses'] else ''}
        
        <h3>Últimas 15 Medições de Telemetria</h3>
        <table>
            <thead>
                <tr>
                    <th>Data/Hora</th>
                    <th>Temperatura</th>
                    <th>Vibração</th>
                    <th>Consumo Elétrico</th>
                </tr>
            </thead>
            <tbody>
                {linhas_tabela}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(html)

    return caminho_arquivo
