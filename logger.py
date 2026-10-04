"""
Logging estruturado do MetalSense.

- Formato JSON (uma linha por evento) para agregadores (Loki, ELK, CloudWatch).
- Streams separados por severidade: DEBUG/INFO -> stdout, WARNING+ -> stderr.
- Correlação por request_id (contextvar preenchida pelo middleware da API).
- Sem handler de arquivo por padrão: em container, o runtime coleta stdout/stderr
  (rotação configurada no docker-compose). Arquivo opcional via METALSENSE_LOG_ARQUIVO.
"""

from __future__ import annotations

import contextvars
import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

_CAMPOS_PADRAO_LOGRECORD = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class FormatadorJSON(logging.Formatter):
    """Serializa o LogRecord como JSON, incluindo campos passados via `extra=`."""

    def format(self, record: logging.LogRecord) -> str:
        evento = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds"),
            "nivel": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", request_id_ctx.get()),
            "pid": record.process,
        }
        for chave, valor in record.__dict__.items():
            if chave not in _CAMPOS_PADRAO_LOGRECORD and chave not in evento and not chave.startswith("_"):
                evento[chave] = valor
        if record.exc_info:
            evento["exc"] = self.formatException(record.exc_info)
        return json.dumps(evento, ensure_ascii=False, default=str)


class FormatadorTexto(logging.Formatter):
    def __init__(self) -> None:
        super().__init__("%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_ctx.get()
        return super().format(record)


class _AbaixoDe(logging.Filter):
    def __init__(self, nivel: int) -> None:
        super().__init__()
        self.nivel = nivel

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.nivel


_configurado = False


def configurar_logging(nivel: str | None = None, json_format: bool | None = None, forcar: bool = False) -> None:
    """Configura o logger raiz. Idempotente (seguro chamar em cada worker/processo)."""
    global _configurado
    if _configurado and not forcar:
        return

    nivel = (nivel or os.environ.get("METALSENSE_LOG_LEVEL", "INFO")).upper()
    if json_format is None:
        json_format = os.environ.get("METALSENSE_LOG_JSON", "true").strip().lower() in {"1", "true", "yes", "on"}
    formatador: logging.Formatter = FormatadorJSON() if json_format else FormatadorTexto()

    raiz = logging.getLogger()
    for h in list(raiz.handlers):
        raiz.removeHandler(h)
    raiz.setLevel(getattr(logging, nivel, logging.INFO))

    saida = logging.StreamHandler(sys.stdout)
    saida.setLevel(logging.DEBUG)
    saida.addFilter(_AbaixoDe(logging.WARNING))
    saida.setFormatter(formatador)

    erros = logging.StreamHandler(sys.stderr)
    erros.setLevel(logging.WARNING)
    erros.setFormatter(formatador)

    raiz.addHandler(saida)
    raiz.addHandler(erros)

    arquivo = os.environ.get("METALSENSE_LOG_ARQUIVO")
    if arquivo:
        rotativo = logging.handlers.RotatingFileHandler(arquivo, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
        rotativo.setFormatter(FormatadorJSON())
        raiz.addHandler(rotativo)

    # Bibliotecas ruidosas
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    _configurado = True


def obter_logger(nome: str) -> logging.Logger:
    return logging.getLogger(f"metalsense.{nome}")


# Instância padrão para compatibilidade retroativa
logger = obter_logger("geral")
