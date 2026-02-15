from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from app.app_layer.interfaces.http.ssau.interface import ScheduleProvider
from app.app_layer.interfaces.time.clock.interface import Clock
from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.domain.entities.schedule_cache import ScheduleCache
from app.domain.entities.user import User

logger = logging.getLogger(__name__)


class ScheduleSyncService:

    def __init__(
        self,
        provider: ScheduleProvider,
        clock: Clock,
    ) -> None:
        self._provider = provider
        self._clock = clock

    async def sync_for_user(
        self,
        uow: UnitOfWork,
        user: User,
        target_date: date,
    ) -> ScheduleCache:
        if user.id is None:
            raise ValueError("User ID is required to store schedule cache.")
        if user.ssau.profile is None:
            raise ValueError("User SSAU profile is required to sync schedule.")

        week_number = AcademicWeekCalculator(
            user.ssau.profile.academic_year_start
        ).get_week_number(target_date)
        logger.info(
            "Sync schedule: user=%s date=%s week=%s year_start=%s",
            user.telegram.chat_id,
            target_date,
            week_number,
            user.ssau.profile.academic_year_start,
        )
        lessons = await self._provider.fetch_week_schedule(user, week_number)

        cache = ScheduleCache(
            user_id=user.id,
            week_number=week_number,
            fetched_at=self._clock.now(),
            lessons=lessons,
        )
        await uow.schedule_cache.upsert(cache)
        return cache

    async def sync_if_stale(
        self,
        uow: UnitOfWork,
        user: User,
        target_date: date,
        max_age: timedelta,
    ) -> ScheduleCache:
        if user.id is None:
            raise ValueError("User ID is required to store schedule cache.")
        if user.ssau.profile is None:
            raise ValueError("User SSAU profile is required to sync schedule.")

        week_number = AcademicWeekCalculator(
            user.ssau.profile.academic_year_start
        ).get_week_number(target_date)
        logger.info(
            "Sync check: user=%s date=%s week=%s year_start=%s",
            user.telegram.chat_id,
            target_date,
            week_number,
            user.ssau.profile.academic_year_start,
        )
        cache = await uow.schedule_cache.get(user.id, week_number)
        if cache is None:
            return await self.sync_for_user(uow, user, target_date)

        now = self._ensure_aware(self._clock.now())
        fetched_at = self._ensure_aware(cache.fetched_at)
        if now - fetched_at < max_age:
            return cache

        return await self.sync_for_user(uow, user, target_date)

    @staticmethod
    def _ensure_aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
