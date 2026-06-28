from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infra.db.settings import DatabaseEngineSettings


def create_engine(settings: DatabaseEngineSettings) -> AsyncEngine:
    _ensure_sqlite_path(settings.url)
    return create_async_engine(settings.url, echo=settings.echo, future=True)


async def database_engine(settings: DatabaseEngineSettings) -> AsyncIterator[AsyncEngine]:
    """DI Resource: создаёт engine и закрывает его (dispose) на shutdown."""
    engine = create_engine(settings)
    try:
        yield engine
    finally:
        await engine.dispose()


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


def _ensure_sqlite_path(database_url: str) -> None:
    prefix = "sqlite+aiosqlite:///"
    if not database_url.startswith(prefix):
        return
    path_part = database_url[len(prefix) :]
    if not path_part or path_part == ":memory:":
        return
    Path(path_part).expanduser().parent.mkdir(parents=True, exist_ok=True)
