"""
API REST Industrial do MetalSense (Hardened para Produção).
Gateway de ingestão de telemetria IoT com autenticação RBAC, validação estrita Pydantic v2,
rate limiting distribuído, probes de orquestração (Liveness/Readiness) e logging auditável.
"""

from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from flask import Flask, request, jsonify, Response, current_app
from pydantic import ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Configuracao
from dados import carregar_dados, salvar_dados
from maquinas import criar_maquina, remover_maquina, registrar_leitura, analisar_maquina
from analytics import calcular_indice_saude
from relatorios import exportar_historico_csv, gerar_relatorio_html
from database import db, verificar_prontidao, aplicar_migracoes
from schemas import TelemetriaPayload, TelemetriaLotePayload, MaquinaCadastroPayload
from security import require_api_key, limiter
from logger import obter_logger, request_id_ctx, configurar_logging

log = obter_logger("api")
INICIO_SISTEMA = time.time()


def create_app(cfg: Optional[Configuracao] = None) -> Flask:
    """Application Factory para ambiente de produção e testes automatizados."""
    if cfg is None:
        cfg = Configuracao.do_ambiente()

    configurar_logging(nivel=cfg.log_level, json_format=cfg.log_json)

    app = Flask(__name__)
    app.config["METALSENSE_CONFIG"] = cfg
    app.config["RATELIMIT_STORAGE_URI"] = cfg.ratelimit_storage_uri
    app.config["RATELIMIT_DEFAULT"] = cfg.ratelimit_global

    # Inicializa Rate Limiter
    limiter.init_app(app)

    # ProxyFix para leitura correta de IPs reais e headers HTTPS atrás de proxies (Nginx/Traefik)
    if cfg.proxies_confiaveis > 0:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=cfg.proxies_confiaveis,
            x_proto=cfg.proxies_confiaveis,
            x_host=cfg.proxies_confiaveis,
            x_prefix=cfg.proxies_confiaveis
        )

    # --------------------------------------------------------------------------
    # Middlewares de Request ID e Auditoria
    # --------------------------------------------------------------------------
    @app.before_request
    def atribuir_request_id():
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_ctx.set(rid)
        request.request_id = rid

    @app.after_request
    def adicionar_headers_seguranca(response: Response):
        response.headers["X-Request-ID"] = getattr(request, "request_id", "-")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # --------------------------------------------------------------------------
    # Handlers Globais de Erro
    # --------------------------------------------------------------------------
    @app.errorhandler(429)
    def ratelimit_handler(e):
        log.warning("rate_limit_excedido", extra={"ip": request.remote_addr, "rota": request.path})
        return jsonify({
            "status": "erro",
            "codigo": 429,
            "mensagem": "Taxa limite de requisições excedida. Reduza o intervalo de envio dos sensores."
        }), 429

    @app.errorhandler(404)
    def not_found_handler(e):
        return jsonify({
            "status": "erro",
            "codigo": 404,
            "mensagem": "Recurso ou rota não encontrada."
        }), 404

    @app.errorhandler(500)
    def internal_error_handler(e):
        log.error("erro_interno_servidor", extra={"rota": request.path, "erro": str(e)}, exc_info=True)
        return jsonify({
            "status": "erro",
            "codigo": 500,
            "mensagem": "Erro interno no processamento do gateway industrial."
        }), 500

    # ==========================================================================
    # PROBES DE ORQUESTRAÇÃO & OBSERVABILIDADE (Kubernetes / Docker)
    # ==========================================================================

    @app.route("/health", methods=["GET"])
    def liveness_probe():
        """Liveness probe: verifica se o processo está ativo e respondendo."""
        uptime = round(time.time() - INICIO_SISTEMA, 2)
        return jsonify({
            "status": "online",
            "liveness": "UP",
            "sistema": "MetalSense Industrial Gateway",
            "versao": "2.0.0-PRO",
            "uptime_segundos": uptime,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    @app.route("/ready", methods=["GET"])
    def readiness_probe():
        """Readiness probe: verifica integridade do banco e versão das migrações."""
        estado = verificar_prontidao(db.engine)
        if estado.get("pronto"):
            return jsonify({
                "status": "READY",
                "detalhes": estado,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 200
        else:
            log.error("readiness_check_falhou", extra={"detalhes": estado})
            return jsonify({
                "status": "NOT_READY",
                "detalhes": estado,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 503

    # ==========================================================================
    # ROTAS PÚBLICAS / CONSULTA
    # ==========================================================================

    @app.route("/api/maquinas", methods=["GET"])
    def listar_maquinas():
        """Retorna máquinas cadastradas e Health Scores consolidados."""
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
        """Retorna detalhes e laudo preditivo completo de um ativo."""
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

        return jsonify({"status": "erro", "codigo": 404, "mensagem": f"Máquina ID {id_maquina} não encontrada"}), 404

    @app.route("/api/relatorios/<int:id_maquina>/html", methods=["GET"])
    def relatorio_html_api(id_maquina: int):
        """Renderiza laudo de auditoria técnica em HTML."""
        dados = carregar_dados()
        for m in dados.get("maquinas", []):
            if m["id"] == id_maquina:
                caminho = gerar_relatorio_html(m)
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                return Response(conteudo, mimetype="text/html")
        return jsonify({"status": "erro", "codigo": 404, "mensagem": "Máquina não encontrada"}), 404

    # ==========================================================================
    # ROTAS PROTEGIDAS (INGESTÃO IOT & GESTÃO DE ATIVOS)
    # ==========================================================================

    @app.route("/api/telemetria", methods=["POST"])
    @limiter.limit("240 per minute")
    @require_api_key(escopos=["dispositivo", "admin"])
    def receber_telemetria_iot():
        """Ingestão pontual de telemetria com validação estrita Pydantic."""
        raw_json = request.get_json(silent=True)
        if raw_json is None:
            return jsonify({
                "status": "erro",
                "codigo": 400,
                "mensagem": "Corpo da requisição deve ser um objeto JSON válido."
            }), 400

        try:
            payload = TelemetriaPayload.model_validate(raw_json)
        except ValidationError as err:
            erros = [{"campo": ".".join(str(loc) for loc in e["loc"]), "erro": e["msg"]} for e in err.errors()]
            log.warning("telemetria_invalida", extra={"erros": erros, "ip": request.remote_addr})
            return jsonify({
                "status": "erro",
                "codigo": 400,
                "mensagem": "Falha na validação do payload de telemetria.",
                "detalhes": erros
            }), 400

        id_maquina = payload.id_maquina
        dados = carregar_dados()
        maquina = next((m for m in dados.get("maquinas", []) if m["id"] == id_maquina), None)

        if not maquina:
            log.warning("maquina_nao_cadastrada", extra={"id_maquina": id_maquina})
            return jsonify({
                "status": "erro",
                "codigo": 404,
                "mensagem": f"Máquina ID {id_maquina} não cadastrada no sistema."
            }), 404

        ts_val = payload.timestamp if payload.timestamp else datetime.now(timezone.utc)
        leitura_dict = {
            "temperatura": payload.temperatura,
            "vibracao": payload.vibracao,
            "consumo": payload.consumo,
            "timestamp": ts_val.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 1. Processamento e inferência preditiva em maquinas.py
        diagnostico = registrar_leitura(dados, id_maquina, leitura=leitura_dict)

        # 2. Persistência de série temporal idempotente no banco relacional (SQLite WAL / PostgreSQL)
        try:
            db.salvar_leitura(
                maquina_id=id_maquina,
                temperatura=payload.temperatura,
                vibracao=payload.vibracao,
                consumo=payload.consumo,
                timestamp=payload.timestamp
            )
        except Exception as ex:
            log.error("falha_salvar_leitura_db", extra={"erro": str(ex)})

        log.info("telemetria_ingerida", extra={
            "id_maquina": id_maquina,
            "temp": payload.temperatura,
            "vib": payload.vibracao,
            "status": diagnostico
        })

        return jsonify({
            "status": "sucesso",
            "id_maquina": id_maquina,
            "diagnostico": diagnostico,
            "leitura": leitura_dict
        }), 200

    @app.route("/api/telemetria/lote", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key(escopos=["dispositivo", "admin"])
    def receber_telemetria_lote():
        """Ingestão em lote de telemetria (buffer offline de gateways de campo)."""
        raw_json = request.get_json(silent=True)
        if raw_json is None:
            return jsonify({
                "status": "erro",
                "codigo": 400,
                "mensagem": "JSON inválido."
            }), 400

        try:
            lote = TelemetriaLotePayload.model_validate(raw_json)
        except ValidationError as err:
            erros = [{"campo": ".".join(str(loc) for loc in e["loc"]), "erro": e["msg"]} for e in err.errors()]
            return jsonify({
                "status": "erro",
                "codigo": 400,
                "mensagem": "Falha na validação do lote de telemetria.",
                "detalhes": erros
            }), 400

        dados = carregar_dados()
        processados = 0
        erros_itens = []

        for idx, item in enumerate(lote.leituras):
            maquina = next((m for m in dados.get("maquinas", []) if m["id"] == item.id_maquina), None)
            if not maquina:
                erros_itens.append({"indice": idx, "id_maquina": item.id_maquina, "erro": "Máquina não encontrada"})
                continue

            ts_item = item.timestamp if item.timestamp else datetime.now(timezone.utc)
            leitura_dict = {
                "temperatura": item.temperatura,
                "vibracao": item.vibracao,
                "consumo": item.consumo,
                "timestamp": ts_item.strftime("%Y-%m-%d %H:%M:%S")
            }
            registrar_leitura(dados, item.id_maquina, leitura=leitura_dict)
            try:
                db.salvar_leitura(
                    maquina_id=item.id_maquina,
                    temperatura=item.temperatura,
                    vibracao=item.vibracao,
                    consumo=item.consumo,
                    timestamp=item.timestamp
                )
            except Exception:
                pass
            processados += 1

        log.info("lote_telemetria_processado", extra={"total": len(lote.leituras), "sucesso": processados})

        return jsonify({
            "status": "sucesso",
            "total_recebido": len(lote.leituras),
            "processados": processados,
            "erros": erros_itens
        }), 200

    @app.route("/api/maquinas", methods=["POST"])
    @require_api_key(escopos=["admin"])
    def cadastrar_nova_maquina():
        """Cadastra nova máquina no parque com validação Pydantic."""
        raw_json = request.get_json(silent=True)
        if raw_json is None:
            return jsonify({"status": "erro", "codigo": 400, "mensagem": "JSON inválido."}), 400

        try:
            payload = MaquinaCadastroPayload.model_validate(raw_json)
        except ValidationError as err:
            return jsonify({
                "status": "erro",
                "codigo": 400,
                "mensagem": "Nome de máquina inválido.",
                "detalhes": err.errors()
            }), 400

        dados = carregar_dados()
        try:
            nova = criar_maquina(dados, payload.nome)
            log.info("maquina_cadastrada", extra={"id": nova["id"], "nome": nova["nome"]})
            return jsonify({
                "status": "sucesso",
                "mensagem": "Máquina cadastrada com sucesso",
                "maquina": nova
            }), 201
        except ValueError as e:
            return jsonify({"status": "erro", "codigo": 400, "mensagem": str(e)}), 400

    @app.route("/api/maquinas/<int:id_maquina>", methods=["DELETE"])
    @require_api_key(escopos=["admin"])
    def deletar_maquina_api(id_maquina: int):
        """Remove máquina e histórico pelo ID."""
        dados = carregar_dados()
        removido = remover_maquina(dados, id_maquina)
        if removido:
            log.info("maquina_deletada", extra={"id": id_maquina})
            return jsonify({
                "status": "sucesso",
                "mensagem": f"Máquina {id_maquina} removida com sucesso"
            }), 200
        return jsonify({
            "status": "erro",
            "codigo": 404,
            "mensagem": f"Máquina ID {id_maquina} não encontrada"
        }), 404

    return app


# Instância padrão para Gunicorn / WSGI
app = create_app()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    log.info(f"Iniciando API MetalSense Gateway em http://{host}:{porta}")
    app.run(host=host, port=porta, debug=False)
