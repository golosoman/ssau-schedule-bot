from __future__ import annotations

from asyncio import run
from logging.config import fileConfig
from os import getenv
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.infra.db import models  # noqa: F401
from app.infra.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./data/ssau_schedule_bot.db"
ENV_FILES = (
    "envs/common.env",
    "envs/local.env",
    "envs/dev.env",
    "envs/prod.env",
    "envs/sensitive.env",
)


def _read_database_url_from_env_files() -> str | None:
    database_url: str | None = None
    project_root = Path(__file__).resolve().parents[1]
    for rel_path in ENV_FILES:
        path = project_root / rel_path
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", maxsplit=1)
            if key.strip() != "DATABASE__URL":
                continue
            database_url = value.strip().strip("'").strip('"')
    return database_url


def _get_database_url() -> str:
    return (
        getenv("ALEMBIC_DATABASE_URL")
        or getenv("DATABASE__URL")
        or _read_database_url_from_env_files()
        or DEFAULT_DATABASE_URL
    )


def _configure_database_url() -> None:
    config.set_main_option("sqlalchemy.url", _get_database_url())


def run_migrations_offline() -> None:
    _configure_database_url()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def _run_migrations(connection) -> None:  # type: ignore[no-untyped-def]
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    _configure_database_url()
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run(run_migrations_online())
