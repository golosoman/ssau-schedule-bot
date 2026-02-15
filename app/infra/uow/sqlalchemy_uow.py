from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.infra.repos import (
    SqlAlchemyNotificationLogRepository,
    SqlAlchemyScheduleCacheRepository,
    SqlAlchemyUserRepository,
)
from app.infra.security.password_cipher import PasswordCipher


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        password_cipher: PasswordCipher,
    ) -> None:
        self._session_factory = session_factory
        self._password_cipher = password_cipher
        self._session: AsyncSession | None = None
        self._committed = False

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session, self._password_cipher)
        self.schedule_cache = SqlAlchemyScheduleCacheRepository(self._session)
        self.notification_log = SqlAlchemyNotificationLogRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is None:
            return
        try:
            if exc:
                await self._session.rollback()
            elif not self._committed:
                await self._session.commit()
        finally:
            await self._session.close()

    async def commit(self) -> None:
        if self._session is None:
            return
        await self._session.commit()
        self._committed = True

    async def rollback(self) -> None:
        if self._session is None:
            return
        await self._session.rollback()
