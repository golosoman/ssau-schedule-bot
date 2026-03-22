from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.app_layer.interfaces.repos.notification_log.interface import (
    INotificationLogRepository,
)
from app.app_layer.interfaces.repos.schedule_cache.interface import (
    IScheduleCacheRepository,
)
from app.app_layer.interfaces.repos.user.interface import IUserRepository
from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.infra.repos import (
    SqlAlchemyNotificationLogRepository,
    SqlAlchemyScheduleCacheRepository,
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        password_cipher: IPasswordCipher,
    ) -> None:
        self._session_factory = session_factory
        self._password_cipher = password_cipher
        self._session: AsyncSession | None = None
        self._committed = False
        self._users: IUserRepository | None = None
        self._schedule_cache: IScheduleCacheRepository | None = None
        self._notification_log: INotificationLogRepository | None = None

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()
        self._users = SqlAlchemyUserRepository(self._session, self._password_cipher)
        self._schedule_cache = SqlAlchemyScheduleCacheRepository(self._session)
        self._notification_log = SqlAlchemyNotificationLogRepository(self._session)
        self._committed = False
        return self

    @property
    def users(self) -> IUserRepository:
        if self._users is None:
            raise RuntimeError("IUnitOfWork is not initialized.")
        return self._users

    @property
    def schedule_cache(self) -> IScheduleCacheRepository:
        if self._schedule_cache is None:
            raise RuntimeError("IUnitOfWork is not initialized.")
        return self._schedule_cache

    @property
    def notification_log(self) -> INotificationLogRepository:
        if self._notification_log is None:
            raise RuntimeError("IUnitOfWork is not initialized.")
        return self._notification_log

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc:
                await self._session.rollback()
            elif not self._committed:
                await self._session.commit()
        finally:
            await self._session.close()
            self._session = None
            self._users = None
            self._schedule_cache = None
            self._notification_log = None

    async def commit(self) -> None:
        if self._session is None:
            return
        await self._session.commit()
        self._committed = True

    async def rollback(self) -> None:
        if self._session is None:
            return
        await self._session.rollback()
