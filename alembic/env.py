from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.database.models import Base  # noqa: E402

config = context.config

# Build a sync (psycopg2) URL for Alembic, independent of the app's async engine.
_raw_url = settings.database_url
_sync_url = (
    _raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    .replace("postgres://", "postgresql+psycopg2://")
)
config.set_main_option("sqlalchemy.url", _sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Fail fast instead of hanging forever if the server can't hand out a connection.
        connect_args={"connect_timeout": 10},
    )
    with connectable.connect() as connection:
        # Critical: if another session holds a lock on alembic_version (e.g. a stale
        # idle-in-transaction connection from a previous crashed deploy), don't wait
        # forever for it — fail loudly after a few seconds instead.
        connection.execute(text("SET lock_timeout = '5s'"))
        connection.execute(text("SET statement_timeout = '30s'"))
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
