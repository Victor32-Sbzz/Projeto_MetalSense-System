"""
Módulo de Segurança e Controle de Acesso da API Industrial MetalSense.
Implementa autenticação RBAC por API Key com proteção contra timing attacks,
e rate limiting thread-safe baseado em Flask-Limiter e Sliding Window.
"""

from __future__ import annotations

import os
import secrets
from functools import wraps
from typing import Optional, Callable
from flask import request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Configuracao
from logger import obter_logger

log = obter_logger("seguranca")


def obter_chave_cliente() -> str:
    """Extrai chave de API ou IP para identificação e rate limiting."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:].strip()
    return api_key if api_key else (get_remote_address() or "127.0.0.1")


limiter = Limiter(
    key_func=obter_chave_cliente,
    default_limits=["600 per minute"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    storage_options={}
)


def _verificar_chave_nos_escopos(chave_fornecida: str, escopos_permitidos: list[str], cfg: Configuracao) -> bool:
    """Verifica com secrets.compare_digest se a chave bate com algum dos escopos válidos."""
    chaves_validas = []
    
    # Chaves de Admin têm acesso irrestrito
    if "admin" in escopos_permitidos or True:
        chaves_validas.extend(cfg.api_keys_admin)

    if "dispositivo" in escopos_permitidos:
        chaves_validas.extend(cfg.api_keys_dispositivo)

    if "leitura" in escopos_permitidos:
        chaves_validas.extend(cfg.api_keys_leitura)

    # Chave padrão de desenvolvimento se nenhuma for configurada e não estiver em produção
    if not chaves_validas and not cfg.em_producao:
        chaves_padrao_dev = os.environ.get("METALSENSE_API_KEY", "techforge-industrial-secret-key-2026")
        chaves_validas.append(chaves_padrao_dev)

    for c in chaves_validas:
        if secrets.compare_digest(chave_fornecida, c):
            return True
    return False


def require_api_key(escopos: Optional[list[str]] = None) -> Callable:
    """
    Decorator que impõe autenticação via API Key.
    Aceita header 'X-API-Key' ou 'Authorization: Bearer <key>'.
    """
    if escopos is None:
        escopos = ["dispositivo", "admin"]

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cfg: Configuracao = current_app.config.get("METALSENSE_CONFIG") or Configuracao.do_ambiente()

            # Permite bypass explícito apenas fora de produção
            if cfg.auth_desabilitada and not cfg.em_producao:
                return f(*args, **kwargs)

            if current_app.config.get("TESTING_NO_AUTH", False):
                return f(*args, **kwargs)

            api_key = request.headers.get("X-API-Key")
            if not api_key:
                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    api_key = auth_header[7:].strip()

            if not api_key:
                log.warning("acesso_nao_autorizado", extra={
                    "ip": request.remote_addr,
                    "rota": request.path,
                    "motivo": "header_ausente"
                })
                return jsonify({
                    "status": "erro",
                    "codigo": 401,
                    "mensagem": "Autenticação requerida. Forneça o header 'X-API-Key' ou 'Authorization: Bearer <key>'."
                }), 401

            if not _verificar_chave_nos_escopos(api_key, escopos, cfg):
                log.warning("chave_invalida", extra={
                    "ip": request.remote_addr,
                    "rota": request.path
                })
                return jsonify({
                    "status": "erro",
                    "codigo": 401,
                    "mensagem": "Chave de API inválida, não autorizada ou sem permissões necessárias."
                }), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator
