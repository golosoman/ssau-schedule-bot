from abc import ABC, abstractmethod

from app.app_layer.interfaces.cache.schedule.dto import CachedWeek


class IScheduleCacheStore(ABC):
    """Порт кэша расписания (driven). Реализация — Valkey, вне транзакции UoW.

    TTL задаётся самой реализацией (конфиг), поэтому возврат значения = оно ещё свежо.
    """

    @abstractmethod
    async def get(self, account_id: int, week_number: int) -> CachedWeek | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, account_id: int, week_number: int, week: CachedWeek) -> None:
        raise NotImplementedError
