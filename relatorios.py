# relatorios.py
"""Módulo de geração de relatórios para máquinas.
Fornece:
- gerar_ordem_servico_texto(maquina)
- exportar_historico_csv(maquina, caminho_destino=None)
- gerar_relatorio_html(maquina, caminho_arquivo=None)
"""

import os
import csv
from typing import Dict, Any, List


def gerar_ordem_servico_texto(maquina: Dict[str, Any]) -> str:
    """Retorna uma string formatada representando a Ordem de Serviço (OS).
    O conteúdo inclui ID, nome da máquina e um resumo das últimas leituras.
    """
    linhas: List[str] = []
    linhas.append("=== ORDEM DE SERVIÇO (OS) ===")
    linhas.append(f"ID da Máquina : {maquina.get('id')}")
    linhas.append(f"Nome          : {maquina.get('nome')}")
    linhas.append(f"Status        : {maquina.get('status')}")
    linhas.append("Leituras recentes:")
    historico = maquina.get('historico', [])[-5:]
    for i, leitura in enumerate(historico, 1):
        linhas.append(
            f"  {i}. {leitura.get('timestamp')} - "
            f"T:{leitura.get('temperatura')}°C "
            f"V:{leitura.get('vibracao')}mm/s "
            f"C:{leitura.get('consumo')}W"
        )
    return "\n".join(linhas)


def exportar_historico_csv(maquina: Dict[str, Any], caminho_destino: str = None) -> str:
    """Exporta o histórico da máquina para um arquivo CSV.
    Se *caminho_destino* não for informado, cria um arquivo na pasta temporária.
    Retorna o caminho absoluto do arquivo gerado.
    """
    if caminho_destino is None:
        caminho_destino = os.path.join(os.getcwd(), f"historico_maquina_{maquina.get('id')}.csv")
    campos = ["timestamp", "temperatura", "vibracao", "consumo"]
    with open(caminho_destino, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for leitura in maquina.get('historico', []):
            writer.writerow({k: leitura.get(k, "") for k in campos})
    return caminho_destino


def gerar_relatorio_html(maquina: Dict[str, Any], caminho_arquivo: str = None) -> str:
    """Gera um relatório em HTML simples para a máquina.
    Se *caminho_arquivo* não for especificado, salva na pasta atual.
    """
    if caminho_arquivo is None:
        caminho_arquivo = os.path.join(os.getcwd(), f"relatorio_maquina_{maquina.get('id')}.html")
    html = f"""
    <!DOCTYPE html>
    <html lang='pt-BR'>
    <head><meta charset='UTF-8'><title>Relatório - {maquina.get('nome')}</title></head>
    <body>
        <h1>Relatório Técnico – {maquina.get('nome')}</h1>
        <p><strong>ID:</strong> {maquina.get('id')}</p>
        <p><strong>Status:</strong> {maquina.get('status')}</p>
        <h2>Histórico de Leituras</h2>
        <table border='1' cellpadding='5' cellspacing='0'>
            <tr><th>Timestamp</th><th>Temperatura (°C)</th><th>Vibração (mm/s)</th><th>Consumo (W)</th></tr>
    """
    for leitura in maquina.get('historico', []):
        html += f"<tr><td>{leitura.get('timestamp')}</td><td>{leitura.get('temperatura')}</td><td>{leitura.get('vibracao')}</td><td>{leitura.get('consumo')}</td></tr>\n"
    html += """
        </table>
    </body>
    </html>
    """
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho_arquivo
