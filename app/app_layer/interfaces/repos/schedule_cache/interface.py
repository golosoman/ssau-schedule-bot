from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.schedule_cache import ScheduleCache


class IScheduleCacheRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int, week_number: int) -> ScheduleCache | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, cache: ScheduleCache) -> None:
        raise NotImplementedError
