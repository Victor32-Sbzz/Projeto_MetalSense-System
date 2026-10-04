"""
Camada de conexão e esquema do MetalSense (SQLAlchemy Core).

Backends suportados:
- PostgreSQL 16 + TimescaleDB (produção): pool de conexões, pre-ping, statement_timeout.
- SQLite em modo WAL (borda/offline e desenvolvimento): múltiplos leitores
  concorrentes + 1 escritor; escritas usam BEGIN IMMEDIATE para evitar o
  deadlock de "upgrade" de lock (SQLITE_BUSY) entre processos.

O esquema é versionado por Alembic (pasta migrations/). As definições de tabela
abaixo são a fonte usada pelo código de acesso; as migrações são a fonte da DDL.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
    text,
)
from sqlalchemy.engine import Connection, Engine, make_url
from sqlalchemy.types import DateTime, TypeDecorator

from config import Configuracao
from logger import obter_logger

log = obter_logger("database")

RAIZ_PROJETO = Path(__file__).resolve().parent
STATUS_VALIDOS = ("sem dados", "normal", "anomalia")


class UTCDateTime(TypeDecorator):
    """Datetime sempre timezone-aware em UTC na aplicação.

    PostgreSQL: TIMESTAMPTZ. SQLite: texto ISO de largura fixa em UTC (ordenação
    lexicográfica == ordenação cronológica).
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise TypeError("UTCDateTime aceita apenas datetime.")
        if value.tzinfo is None:
            raise ValueError("Datetime sem fuso horário recusado (use UTC/aware).")
        value = value.astimezone(timezone.utc)
        return value.replace(tzinfo=None) if dialect.name == "sqlite" else value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


metadata = MetaData()

maquinas = Table(
    "maquinas",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nome", String(100), nullable=False),
    Column("status", String(20), nullable=False, server_default="sem dados"),
    Column("diagnostico", String(1000), nullable=True),
    Column("total_leituras", BigInteger, nullable=False, server_default="0"),
    Column("ultima_leitura_em", UTCDateTime(), nullable=True),
    Column("criado_em", UTCDateTime(), nullable=False),
    Column("atualizado_em", UTCDateTime(), nullable=False),
    CheckConstraint("status IN ('sem dados', 'normal', 'anomalia')", name="ck_maquinas_status"),
    sqlite_autoincrement=True,  # IDs nunca são reutilizados (dispositivo antigo não grava em máquina nova)
)

leituras = Table(
    "leituras",
    metadata,
    Column("maquina_id", Integer, ForeignKey("maquinas.id", ondelete="CASCADE"), primary_key=True),
    # PK composta (maquina_id, ts): requisito de hypertable do TimescaleDB e
    # garante idempotência — retransmissões do mesmo dispositivo não duplicam dados.
    Column("ts", UTCDateTime(), primary_key=True),
    Column("temperatura", Float, nullable=False),
    Column("vibracao", Float, nullable=False),
    Column("consumo", Float, nullable=False),
    Column("recebido_em", UTCDateTime(), nullable=False),
)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------------------

def criar_engine(cfg: Configuracao) -> Engine:
    url = make_url(cfg.database_url)
    backend = url.get_backend_name()

    if backend == "sqlite":
        if url.database in (None, "", ":memory:"):
            raise RuntimeError("SQLite em memória não é suportado (cada conexão do pool veria um banco diferente).")
        engine = create_engine(
            url,
            pool_size=cfg.db_pool_size,
            max_overflow=cfg.db_max_overflow,
            pool_timeout=cfg.db_pool_timeout_s,
            connect_args={"timeout": 30, "check_same_thread": False},
        )
        _instrumentar_sqlite(engine, cfg.sqlite_synchronous)
    elif backend == "postgresql":
        engine = create_engine(
            url,
            pool_size=cfg.db_pool_size,
            max_overflow=cfg.db_max_overflow,
            pool_timeout=cfg.db_pool_timeout_s,
            pool_pre_ping=True,      # descarta conexões mortas após restart/failover do banco
            pool_recycle=1800,
            connect_args={
                "connect_timeout": 5,
                "application_name": "metalsense",
                "options": f"-c statement_timeout={cfg.db_statement_timeout_ms}",
            },
        )
    else:
        raise RuntimeError(f"Backend de banco não suportado: {backend}")

    log.info("engine_criada", extra={"backend": backend, "pool_size": cfg.db_pool_size})
    return engine


def _instrumentar_sqlite(engine: Engine, synchronous: str) -> None:
    @event.listens_for(engine, "connect")
    def _ao_conectar(dbapi_conn, _registro):  # pragma: no cover - executado pelo driver
        # Desliga o BEGIN implícito do pysqlite: o SQLAlchemy passa a controlar a transação.
        dbapi_conn.isolation_level = None
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute(f"PRAGMA synchronous={synchronous}")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA busy_timeout=15000")
        cur.close()

    @event.listens_for(engine, "begin")
    def _ao_iniciar(conn: Connection):  # pragma: no cover - executado pelo driver
        modo = conn.get_execution_options().get("sqlite_begin", "DEFERRED")
        conn.exec_driver_sql(f"BEGIN {modo}")


@contextmanager
def transacao_escrita(engine: Engine) -> Iterator[Connection]:
    """Transação de escrita. No SQLite adquire o lock de escrita já no BEGIN."""
    with engine.connect() as conn:
        if engine.dialect.name == "sqlite":
            conn.execution_options(sqlite_begin="IMMEDIATE")
        with conn.begin():
            yield conn


@contextmanager
def transacao_leitura(engine: Engine) -> Iterator[Connection]:
    """Transação somente leitura com snapshot consistente."""
    with engine.connect() as conn:
        with conn.begin():
            yield conn


# ------------------------------------------------------------------------------
# Migrações / prontidão
# ------------------------------------------------------------------------------

def _config_alembic(database_url: str):
    from alembic.config import Config

    cfg = Config(str(RAIZ_PROJETO / "alembic.ini"))
    cfg.set_main_option("script_location", str(RAIZ_PROJETO / "migrations"))
    cfg.attributes["database_url"] = database_url
    return cfg


@lru_cache(maxsize=1)
def revisao_head() -> str:
    """Revisão Alembic esperada pelo código desta versão."""
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(_config_alembic("sqlite://"))
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Migrações com múltiplos heads: {heads}")
    return heads[0]


def aplicar_migracoes(database_url: str, revisao: str = "head") -> None:
    from alembic import command

    command.upgrade(_config_alembic(database_url), revisao)


def reverter_migracoes(database_url: str, revisao: str) -> None:
    from alembic import command

    command.downgrade(_config_alembic(database_url), revisao)


def verificar_prontidao(engine: Engine) -> dict:
    """Usado pelo probe /ready: banco acessível E esquema na revisão esperada."""
    resultado = {"banco": "falha", "migracao": "desconhecida"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            resultado["banco"] = "ok"
            try:
                atual = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            except Exception:
                atual = None
        esperado = revisao_head()
        resultado["migracao"] = "ok" if atual == esperado else f"pendente (atual={atual}, esperado={esperado})"
    except Exception as exc:  # banco fora do ar, credencial errada, etc.
        log.warning("prontidao_falhou", extra={"erro": type(exc).__name__})
    resultado["pronto"] = resultado["banco"] == "ok" and resultado["migracao"] == "ok"
    return resultado


# ------------------------------------------------------------------------------
# Repositório de Persistência e Wrapper de Compatibilidade
# ------------------------------------------------------------------------------

_engine_global: Optional[Engine] = None


def obter_engine_padrao() -> Engine:
    """Retorna uma instância singleton da engine padrão baseada na configuração."""
    global _engine_global
    if _engine_global is None:
        cfg = Configuracao.do_ambiente()
        _engine_global = criar_engine(cfg)
    return _engine_global


class DatabaseManager:
    """Wrapper de alta conveniência para operações de banco e compatibilidade."""

    def __init__(self, engine: Optional[Engine] = None):
        self._engine = engine

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = obter_engine_padrao()
        return self._engine

    def check_health(self) -> bool:
        """Verifica se o banco está pronto e funcional."""
        try:
            with self.engine.connect() as conn:
                res = conn.execute(text("SELECT 1")).scalar()
                return res == 1
        except Exception:
            return False

    def salvar_leitura(
        self,
        maquina_id: int,
        temperatura: float,
        vibracao: float,
        consumo: float,
        timestamp: Optional[datetime | str] = None
    ) -> None:
        """Grava uma leitura na tabela leituras com idempotência e atualização de métricas na máquina."""
        agora = agora_utc()
        if timestamp is None:
            ts_dt = agora
        elif isinstance(timestamp, str):
            try:
                ts_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if ts_dt.tzinfo is None:
                    ts_dt = ts_dt.replace(tzinfo=timezone.utc)
            except ValueError:
                ts_dt = agora
        else:
            ts_dt = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)

        with transacao_escrita(self.engine) as conn:
            # 1. Garante que a máquina exista
            conn.execute(
                text("""
                    INSERT INTO maquinas (id, nome, status, criado_em, atualizado_em)
                    VALUES (:id, :nome, 'sem dados', :criado_em, :atualizado_em)
                    ON CONFLICT(id) DO UPDATE SET
                        atualizado_em = :atualizado_em
                """),
                {
                    "id": maquina_id,
                    "nome": f"Máquina {maquina_id}",
                    "criado_em": agora,
                    "atualizado_em": agora
                }
            )

            # 2. Insere a leitura (idempotente)
            if self.engine.dialect.name == "postgresql":
                sql_leitura = """
                    INSERT INTO leituras (maquina_id, ts, temperatura, vibracao, consumo, recebido_em)
                    VALUES (:maquina_id, :ts, :temperatura, :vibracao, :consumo, :recebido_em)
                    ON CONFLICT (maquina_id, ts) DO UPDATE SET
                        temperatura = excluded.temperatura,
                        vibracao = excluded.vibracao,
                        consumo = excluded.consumo;
                """
            else:
                sql_leitura = """
                    INSERT OR REPLACE INTO leituras (maquina_id, ts, temperatura, vibracao, consumo, recebido_em)
                    VALUES (:maquina_id, :ts, :temperatura, :vibracao, :consumo, :recebido_em);
                """

            conn.execute(
                text(sql_leitura),
                {
                    "maquina_id": maquina_id,
                    "ts": ts_dt,
                    "temperatura": temperatura,
                    "vibracao": vibracao,
                    "consumo": consumo,
                    "recebido_em": agora
                }
            )

            # 3. Atualiza contadores e timestamp da máquina
            conn.execute(
                text("""
                    UPDATE maquinas
                    SET total_leituras = (SELECT COUNT(*) FROM leituras WHERE maquina_id = :id),
                        ultima_leitura_em = :ts,
                        atualizado_em = :agora
                    WHERE id = :id
                """),
                {"id": maquina_id, "ts": ts_dt, "agora": agora}
            )

    def obter_historico(self, maquina_id: int, limit: int = 50) -> list[dict]:
        """Obtém as últimas N leituras em ordem cronológica."""
        with transacao_leitura(self.engine) as conn:
            res = conn.execute(
                text("""
                    SELECT ts, temperatura, vibracao, consumo
                    FROM leituras
                    WHERE maquina_id = :id
                    ORDER BY ts DESC
                    LIMIT :limit
                """),
                {"id": maquina_id, "limit": limit}
            ).fetchall()

            # Retorna em ordem cronológica crescente
            historico = []
            for r in reversed(res):
                historico.append({
                    "timestamp": r[0].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[0], "strftime") else str(r[0]),
                    "temperatura": float(r[1]),
                    "vibracao": float(r[2]),
                    "consumo": float(r[3]),
                })
            return historico


db = DatabaseManager()
