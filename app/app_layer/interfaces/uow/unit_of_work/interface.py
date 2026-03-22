from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from app.app_layer.interfaces.repos.notification_log.interface import (
    INotificationLogRepository,
)
from app.app_layer.interfaces.repos.schedule_cache.interface import (
    IScheduleCacheRepository,
)
from app.app_layer.interfaces.repos.user.interface import IUserRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def schedule_cache(self) -> IScheduleCacheRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def notification_log(self) -> INotificationLogRepository:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
