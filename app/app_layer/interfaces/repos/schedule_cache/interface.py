from __future__ import annotations

from typing import Protocol

from app.domain.entities.schedule_cache import ScheduleCache


class ScheduleCacheRepository(Protocol):
    async def get(self, user_id: int, week_number: int) -> ScheduleCache | None:
        ...

    async def upsert(self, cache: ScheduleCache) -> None:
        ...
