import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from app.di import Container
from app.infra.db import models  # noqa: F401
from app.infra.db.base import Base


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def main() -> None:
    container = Container()
    engine = container.engine()
    await init_db(engine)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
