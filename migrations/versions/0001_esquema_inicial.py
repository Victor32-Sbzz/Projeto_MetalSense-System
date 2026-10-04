"""Esquema inicial: maquinas + leituras (hypertable TimescaleDB quando disponível).

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    postgres = bind.dialect.name == "postgresql"

    op.create_table(
        "maquinas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="sem dados"),
        sa.Column("diagnostico", sa.String(1000), nullable=True),
        sa.Column("total_leituras", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("ultima_leitura_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('sem dados', 'normal', 'anomalia')", name="ck_maquinas_status"),
        sqlite_autoincrement=True,
    )

    op.create_table(
        "leituras",
        sa.Column("maquina_id", sa.Integer, sa.ForeignKey("maquinas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("temperatura", sa.Float, nullable=False),
        sa.Column("vibracao", sa.Float, nullable=False),
        sa.Column("consumo", sa.Float, nullable=False),
        sa.Column("recebido_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("maquina_id", "ts", name="pk_leituras"),
    )

    if postgres:
        timescale = bind.execute(
            sa.text("SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb'")
        ).scalar()
        if timescale:
            op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
            op.execute(
                "SELECT create_hypertable('leituras', 'ts', "
                "chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE)"
            )
        else:
            op.create_index("ix_leituras_ts", "leituras", ["ts"])
    else:
        op.create_index("ix_leituras_ts", "leituras", ["ts"])


def downgrade() -> None:
    op.drop_table("leituras")
    op.drop_table("maquinas")
