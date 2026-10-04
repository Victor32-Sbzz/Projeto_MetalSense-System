"""Ambiente de execução das migrações Alembic do MetalSense."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import metadata  # noqa: E402
from logger import configurar_logging, obter_logger  # noqa: E402

configurar_logging()
log = obter_logger("migracoes")

config = context.config
target_metadata = metadata


def _url() -> str:
    url = config.attributes.get("database_url") or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Defina DATABASE_URL para executar migrações.")
    return url


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = _url()
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
    log.info("migracoes_aplicadas", extra={"backend": engine.dialect.name})


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
