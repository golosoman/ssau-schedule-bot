from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.app_layer.interfaces.http.ssau.interface import IScheduleProvider
from app.app_layer.interfaces.services.schedule.schedule_sync.dto.input import (
    ScheduleSyncForUserInputDTO,
    ScheduleSyncIfStaleInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.dto.output import (
    ScheduleSyncForUserOutputDTO,
    ScheduleSyncIfStaleOutputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.time.clock.interface import IClock
from app.domain.entities.schedule_cache import ScheduleCache

logger = logging.getLogger(__name__)


class ScheduleSyncService(IScheduleSyncService):
    def __init__(
        self,
        provider: IScheduleProvider,
        clock: IClock,
        week_calculator: IWeekCalculatorService,
    ) -> None:
        self._provider = provider
        self._clock = clock
        self._week_calculator = week_calculator

    async def sync_for_user(
        self,
        input_dto: ScheduleSyncForUserInputDTO,
    ) -> ScheduleSyncForUserOutputDTO:
        uow = input_dto.uow
        user = input_dto.user
        target_date = input_dto.target_date

        if user.id is None:
            raise ValueError("User ID is required to store schedule cache.")
        if user.ssau.profile is None:
            raise ValueError("User SSAU profile is required to sync schedule.")

        week_number = self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=user.ssau.profile.profile_details.academic_year_start,
                target_date=target_date,
            )
        ).week_number
        logger.info(
            "Sync schedule: user=%s date=%s week=%s year_start=%s",
            user.telegram.chat_id,
            target_date,
            week_number,
            user.ssau.profile.profile_details.academic_year_start,
        )
        lessons = await self._provider.fetch_week_schedule(user, week_number)

        cache = ScheduleCache(
            user_id=user.id,
            week_number=week_number,
            fetched_at=self._clock.now(),
            lessons=lessons,
        )
        await uow.schedule_cache.upsert(cache)
        return ScheduleSyncForUserOutputDTO(cache=cache)

    async def sync_if_stale(
        self,
        input_dto: ScheduleSyncIfStaleInputDTO,
    ) -> ScheduleSyncIfStaleOutputDTO:
        uow = input_dto.uow
        user = input_dto.user
        target_date = input_dto.target_date
        max_age = input_dto.max_age

        if user.id is None:
            raise ValueError("User ID is required to store schedule cache.")
        if user.ssau.profile is None:
            raise ValueError("User SSAU profile is required to sync schedule.")

        week_number = self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=user.ssau.profile.profile_details.academic_year_start,
                target_date=target_date,
            )
        ).week_number
        logger.info(
            "Sync check: user=%s date=%s week=%s year_start=%s",
            user.telegram.chat_id,
            target_date,
            week_number,
            user.ssau.profile.profile_details.academic_year_start,
        )
        cache = await uow.schedule_cache.get(user.id, week_number)
        if cache is None:
            synced = await self.sync_for_user(
                ScheduleSyncForUserInputDTO(
                    uow=uow,
                    user=user,
                    target_date=target_date,
                )
            )
            return ScheduleSyncIfStaleOutputDTO(cache=synced.cache)

        now = self._ensure_aware(self._clock.now())
        fetched_at = self._ensure_aware(cache.fetched_at)
        if now - fetched_at < max_age:
            return ScheduleSyncIfStaleOutputDTO(cache=cache)

        synced = await self.sync_for_user(
            ScheduleSyncForUserInputDTO(
                uow=uow,
                user=user,
                target_date=target_date,
            )
        )
        return ScheduleSyncIfStaleOutputDTO(cache=synced.cache)

    @staticmethod
    def _ensure_aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
