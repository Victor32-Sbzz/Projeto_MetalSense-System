"""
Configuração centralizada do MetalSense (12-factor: tudo via variáveis de ambiente).

Nenhum segredo possui valor padrão no código. Em METALSENSE_ENV=production a
aplicação se recusa a iniciar sem credenciais configuradas (fail-closed).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


def _bool(valor: Optional[str], padrao: bool = False) -> bool:
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "sim", "on"}


def _int(nome: str, padrao: int) -> int:
    bruto = os.environ.get(nome)
    if bruto is None or bruto.strip() == "":
        return padrao
    try:
        return int(bruto)
    except ValueError as exc:
        raise RuntimeError(f"Variável de ambiente {nome} deve ser inteira (recebido: {bruto!r}).") from exc


def _lista(nome: str) -> tuple[str, ...]:
    bruto = os.environ.get(nome, "")
    return tuple(item.strip() for item in bruto.split(",") if item.strip())


@dataclass(frozen=True)
class Configuracao:
    """Parâmetros de execução. Instanciar via `Configuracao.do_ambiente()`."""

    ambiente: str = "development"

    # --- Persistência --------------------------------------------------------
    # SQLite (WAL) para borda/offline; PostgreSQL/TimescaleDB em produção.
    database_url: str = "sqlite:///metalsense.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout_s: int = 10
    db_statement_timeout_ms: int = 5000
    sqlite_synchronous: str = "NORMAL"  # NORMAL (WAL: íntegro, pode perder últimos commits em queda de energia) | FULL

    # --- Análise ---------------------------------------------------------------
    janela_analise: int = 100          # nº de leituras recentes usadas na avaliação estatística
    limite_historico_painel: int = 500  # nº de leituras carregadas por máquina no dashboard

    # --- Segurança da API ------------------------------------------------------
    api_keys_dispositivo: tuple[str, ...] = field(default_factory=tuple)
    api_keys_leitura: tuple[str, ...] = field(default_factory=tuple)
    api_keys_admin: tuple[str, ...] = field(default_factory=tuple)
    auth_desabilitada: bool = False     # só é aceito fora de produção
    proxies_confiaveis: int = 0         # nº de proxies reversos à frente da API (ProxyFix)
    max_payload_bytes: int = 256 * 1024
    max_itens_lote: int = 500
    tolerancia_futuro_s: int = 300      # relógio do dispositivo adiantado aceitável
    idade_maxima_leitura_s: int = 30 * 24 * 3600  # buffer offline máximo aceito (30 dias)

    # --- Rate limiting ---------------------------------------------------------
    ratelimit_storage_uri: str = "memory://"
    ratelimit_global: str = "600 per minute"         # por IP de origem
    ratelimit_telemetria: str = "240 per minute"     # por credencial
    ratelimit_lote: str = "30 per minute"            # por credencial

    # --- Observabilidade -------------------------------------------------------
    log_level: str = "INFO"
    log_json: bool = True

    # --- Exibição ---------------------------------------------------------------
    fuso_exibicao: str = "America/Sao_Paulo"
    fuso_legado: str = "America/Sao_Paulo"  # fuso assumido para timestamps sem offset do dados.json antigo

    @property
    def em_producao(self) -> bool:
        return self.ambiente == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @classmethod
    def do_ambiente(cls, **sobrescritas) -> "Configuracao":
        valores = dict(
            ambiente=os.environ.get("METALSENSE_ENV", "development").strip().lower(),
            database_url=os.environ.get("DATABASE_URL", "sqlite:///metalsense.db"),
            db_pool_size=_int("DB_POOL_SIZE", 5),
            db_max_overflow=_int("DB_MAX_OVERFLOW", 10),
            db_pool_timeout_s=_int("DB_POOL_TIMEOUT_S", 10),
            db_statement_timeout_ms=_int("DB_STATEMENT_TIMEOUT_MS", 5000),
            sqlite_synchronous=os.environ.get("SQLITE_SYNCHRONOUS", "NORMAL").upper(),
            janela_analise=_int("METALSENSE_JANELA_ANALISE", 100),
            limite_historico_painel=_int("METALSENSE_LIMITE_HISTORICO_PAINEL", 500),
            api_keys_dispositivo=_lista("METALSENSE_API_KEYS_DISPOSITIVO"),
            api_keys_leitura=_lista("METALSENSE_API_KEYS_LEITURA"),
            api_keys_admin=_lista("METALSENSE_API_KEYS_ADMIN"),
            auth_desabilitada=_bool(os.environ.get("METALSENSE_AUTH_DESABILITADA")),
            proxies_confiaveis=_int("METALSENSE_PROXIES_CONFIAVEIS", 0),
            max_payload_bytes=_int("METALSENSE_MAX_PAYLOAD_BYTES", 256 * 1024),
            max_itens_lote=_int("METALSENSE_MAX_ITENS_LOTE", 500),
            tolerancia_futuro_s=_int("METALSENSE_TOLERANCIA_FUTURO_S", 300),
            idade_maxima_leitura_s=_int("METALSENSE_IDADE_MAXIMA_LEITURA_S", 30 * 24 * 3600),
            ratelimit_storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
            ratelimit_global=os.environ.get("RATELIMIT_GLOBAL", "600 per minute"),
            ratelimit_telemetria=os.environ.get("RATELIMIT_TELEMETRIA", "240 per minute"),
            ratelimit_lote=os.environ.get("RATELIMIT_LOTE", "30 per minute"),
            log_level=os.environ.get("METALSENSE_LOG_LEVEL", "INFO").upper(),
            log_json=_bool(os.environ.get("METALSENSE_LOG_JSON"), padrao=True),
            fuso_exibicao=os.environ.get("METALSENSE_FUSO_EXIBICAO", "America/Sao_Paulo"),
            fuso_legado=os.environ.get("METALSENSE_FUSO_LEGADO", "America/Sao_Paulo"),
        )
        valores.update(sobrescritas)
        cfg = cls(**valores)
        cfg.validar()
        return cfg

    def validar(self) -> None:
        if self.sqlite_synchronous not in {"NORMAL", "FULL", "EXTRA"}:
            raise RuntimeError("SQLITE_SYNCHRONOUS deve ser NORMAL, FULL ou EXTRA.")
        if self.janela_analise < 3:
            raise RuntimeError("METALSENSE_JANELA_ANALISE deve ser >= 3.")
        if self.em_producao and self.auth_desabilitada:
            raise RuntimeError("METALSENSE_AUTH_DESABILITADA não é permitido em produção.")
