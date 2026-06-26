from app.app_layer.interfaces.services.schedule.daily_schedule.dto import (
    DailyScheduleServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.daily_schedule.interface import (
    IDailyScheduleService,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.dto import (
    ScheduleSyncIfStaleInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.use_cases.get_schedule_for_date.dto import (
    GetScheduleForDateUseCaseInputDTO,
    GetScheduleForDateUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.get_schedule_for_date.interface import (
    IGetScheduleForDateUseCase,
)


class GetScheduleForDateUseCase(IGetScheduleForDateUseCase):
    """Расписание пользователя на конкретную дату: синк кэша (если устарел),
    расчёт номера недели, фильтрация пар по дате/неделе/подгруппе."""

    def __init__(
        self,
        schedule_sync_service: IScheduleSyncService,
        week_calculator: IWeekCalculatorService,
        daily_schedule_service: IDailyScheduleService,
    ) -> None:
        self._schedule_sync_service = schedule_sync_service
        self._week_calculator = week_calculator
        self._daily_schedule_service = daily_schedule_service

    async def execute(
        self,
        input_dto: GetScheduleForDateUseCaseInputDTO,
    ) -> GetScheduleForDateUseCaseOutputDTO:
        account = input_dto.account
        profile = account.ssau_profile
        if profile is None:
            raise RuntimeError("Provisioned profile is required to resolve schedule.")

        target_date = input_dto.target_date
        cache = (
            await self._schedule_sync_service.sync_if_stale(
                ScheduleSyncIfStaleInputDTO(account=account, target_date=target_date)
            )
        ).cache
        week_number = self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=profile.academic_year_start,
                target_date=target_date,
            )
        ).week_number
        lessons = self._daily_schedule_service.filter_for_date(
            DailyScheduleServiceInputDTO(
                lessons=cache.lessons,
                target_date=target_date,
                week_number=week_number,
                subgroup=profile.subgroup,
            )
        ).lessons
        return GetScheduleForDateUseCaseOutputDTO(lessons=lessons)
