from __future__ import annotations

from typing import Protocol

from app.app_layer.interfaces.repos.notification_log.interface import (
    NotificationLogRepository,
)
from app.app_layer.interfaces.repos.schedule_cache.interface import (
    ScheduleCacheRepository,
)
from app.app_layer.interfaces.repos.user.interface import UserRepository


class UnitOfWork(Protocol):
    users: UserRepository
    schedule_cache: ScheduleCacheRepository
    notification_log: NotificationLogRepository

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc, tb) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
