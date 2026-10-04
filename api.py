"""
API REST Industrial do MetalSense.
Permite integração direta de sensores IoT (ESP32, Raspberry Pi, Gateways industriais)
e consumo de dados por sistemas MES, SCADA e dashboards externos.
"""

from flask import Flask, request, jsonify, send_file, Response
from dados import carregar_dados, salvar_dados
from maquinas import criar_maquina, remover_maquina, registrar_leitura, analisar_maquina
from analytics import calcular_indice_saude
from relatorios import exportar_historico_csv, gerar_relatorio_html
import os

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def healthcheck():
    """Verifica a integridade da API."""
    return jsonify({
        "status": "online",
        "sistema": "MetalSense - TechForge",
        "versao": "2.0.0-PRO"
    }), 200


@app.route("/api/maquinas", methods=["GET"])
def listar_maquinas():
    """Retorna todas as máquinas cadastradas e seus respectivos Health Scores."""
    dados = carregar_dados()
    resumo = []
    for m in dados.get("maquinas", []):
        historico = m.get("historico", [])
        saude = calcular_indice_saude(historico)
        resumo.append({
            "id": m["id"],
            "nome": m["nome"],
            "status": m.get("status", "sem dados"),
            "health_score": saude["score"],
            "classificacao_saude": saude["classificacao"],
            "total_leituras": len(historico),
            "ultima_leitura": historico[-1] if historico else None
        })
    return jsonify({"total": len(resumo), "maquinas": resumo}), 200


@app.route("/api/maquinas/<int:id_maquina>", methods=["GET"])
def obter_maquina(id_maquina: int):
    """Retorna detalhes, telemetria e diagnóstico completo de uma máquina."""
    dados = carregar_dados()
    for m in dados.get("maquinas", []):
        if m["id"] == id_maquina:
            historico = m.get("historico", [])
            saude = calcular_indice_saude(historico)
            diagnostico = analisar_maquina(dados, id_maquina)
            return jsonify({
                "maquina": m,
                "analise_preditiva": saude,
                "diagnostico_status": diagnostico
            }), 200

    return jsonify({"erro": f"Máquina ID {id_maquina} não encontrada"}), 404


@app.route("/api/maquinas", methods=["POST"])
def cadastrar_nova_maquina():
    """Cadastra uma nova máquina no sistema."""
    payload = request.get_json(silent=True) or {}
    nome = payload.get("nome", "").strip()

    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório."}), 400

    dados = carregar_dados()
    try:
        nova = criar_maquina(dados, nome)
        return jsonify({"mensagem": "Máquina cadastrada com sucesso", "maquina": nova}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/maquinas/<int:id_maquina>", methods=["DELETE"])
def deletar_maquina_api(id_maquina: int):
    """Remove uma máquina pelo ID."""
    dados = carregar_dados()
    removido = remover_maquina(dados, id_maquina)
    if removido:
        return jsonify({"mensagem": f"Máquina {id_maquina} removida com sucesso"}), 200
    return jsonify({"erro": f"Máquina ID {id_maquina} não encontrada"}), 404


@app.route("/api/telemetria", methods=["POST"])
def receber_telemetria_iot():
    """
    Endpoint principal para ingestão de dados de sensores IoT (ESP32, Raspberry Pi, etc).
    Payload esperado:
    {
        "id_maquina": 1,
        "temperatura": 65.4,
        "vibracao": 3.2,
        "consumo": 310.0,
        "timestamp": "2026-10-04 18:00:00"  (opcional)
    }
    """
    payload = request.get_json(silent=True) or {}
    id_maquina = payload.get("id_maquina")

    if not id_maquina:
        return jsonify({"erro": "Campo 'id_maquina' é obrigatório"}), 400

    dados = carregar_dados()
    maquina_existe = any(m["id"] == id_maquina for m in dados.get("maquinas", []))
    if not maquina_existe:
        return jsonify({"erro": f"Máquina ID {id_maquina} não cadastrada."}), 404

    leitura = {
        "temperatura": float(payload.get("temperatura", 0.0)),
        "vibracao": float(payload.get("vibracao", 0.0)),
        "consumo": float(payload.get("consumo", 0.0))
    }
    if "timestamp" in payload:
        leitura["timestamp"] = str(payload["timestamp"])

    resultado = registrar_leitura(dados, id_maquina, leitura=leitura)
    return jsonify({
        "status": "recebido",
        "id_maquina": id_maquina,
        "diagnostico": resultado,
        "leitura_processada": leitura
    }), 200


@app.route("/api/relatorios/<int:id_maquina>/html", methods=["GET"])
def relatorio_html_api(id_maquina: int):
    """Renderiza laudo técnico HTML."""
    dados = carregar_dados()
    for m in dados.get("maquinas", []):
        if m["id"] == id_maquina:
            caminho = gerar_relatorio_html(m)
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            return Response(conteudo, mimetype="text/html")
    return jsonify({"erro": "Máquina não encontrada"}), 404


if __name__ == "__main__":
    print("\n🚀 INICIANDO API REST METALSENSE (GATEWAY IOT)")
    print("📡 Endpoints ativos em: http://127.0.0.1:5000")
    print("📘 Rota de Ingestão: POST /api/telemetria")
    print("📋 Rota de Consulta: GET /api/maquinas\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
