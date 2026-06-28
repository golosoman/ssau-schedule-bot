from datetime import datetime, time, timedelta

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.app_layer.interfaces.schedule.upcoming_lesson.dto import UpcomingLessonDTO
from app.app_layer.interfaces.services.schedule.schedule_sync.dto import (
    ScheduleSyncIfStaleInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.upcoming_lesson.dto import (
    UpcomingLessonServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.upcoming_lesson.interface import (
    IUpcomingLessonService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.dto import (
    GetUpcomingLessonUseCaseInputDTO,
    GetUpcomingLessonUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.interface import (
    IGetUpcomingLessonUseCase,
)
from app.domain.constants import DAYS_IN_WEEK
from app.domain.entities.account.ssau_profile import SsauProfileEntity


class GetUpcomingLessonUseCase(IGetUpcomingLessonUseCase):
    """Ближайшая пара пользователя: ищет в текущей неделе, при отсутствии —
    откатывается на ближайший понедельник следующей недели."""

    def __init__(
        self,
        schedule_sync_service: IScheduleSyncService,
        week_calculator: IWeekCalculatorService,
        upcoming_lesson_service: IUpcomingLessonService,
    ) -> None:
        self._schedule_sync_service = schedule_sync_service
        self._week_calculator = week_calculator
        self._upcoming_lesson_service = upcoming_lesson_service

    async def execute(
        self,
        input_dto: GetUpcomingLessonUseCaseInputDTO,
    ) -> GetUpcomingLessonUseCaseOutputDTO:
        account = input_dto.account
        profile = account.ssau_profile
        if profile is None:
            raise RuntimeError("Provisioned profile is required to resolve upcoming lesson.")

        now_local = input_dto.now_local
        lesson = await self._find_in_week(account, profile, now_local)
        if lesson is None:
            days_until_monday = (DAYS_IN_WEEK + 1) - now_local.isoweekday()
            next_week_date = now_local.date() + timedelta(days=days_until_monday)
            next_week_local = datetime.combine(next_week_date, time.min, tzinfo=now_local.tzinfo)
            lesson = await self._find_in_week(account, profile, next_week_local)

        return GetUpcomingLessonUseCaseOutputDTO(upcoming_lesson=lesson)

    async def _find_in_week(
        self,
        account: AccountViewDTO,
        profile: SsauProfileEntity,
        when: datetime,
    ) -> UpcomingLessonDTO | None:
        cache = (
            await self._schedule_sync_service.sync_if_stale(
                ScheduleSyncIfStaleInputDTO(account=account, target_date=when.date())
            )
        ).cache
        week_number = self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=profile.academic_year_start,
                target_date=when.date(),
            )
        ).week_number
        return self._upcoming_lesson_service.find_next(
            UpcomingLessonServiceInputDTO(
                lessons=cache.lessons,
                now_local=when,
                week_number=week_number,
                subgroup=profile.subgroup,
            )
        ).upcoming_lesson
