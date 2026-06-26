from app.app_layer.interfaces.services.schedule.schedule_sync.dto import (
    ScheduleSyncForUserInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.use_cases.refresh_schedule.dto import (
    RefreshScheduleUseCaseInputDTO,
    RefreshScheduleUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.refresh_schedule.interface import (
    IRefreshScheduleUseCase,
)


class RefreshScheduleUseCase(IRefreshScheduleUseCase):
    """Принудительное обновление расписания пользователя (force-синк кэша из СГАУ)."""

    def __init__(self, schedule_sync_service: IScheduleSyncService) -> None:
        self._schedule_sync_service = schedule_sync_service

    async def execute(
        self,
        input_dto: RefreshScheduleUseCaseInputDTO,
    ) -> RefreshScheduleUseCaseOutputDTO:
        cache = (
            await self._schedule_sync_service.sync_for_user(
                ScheduleSyncForUserInputDTO(
                    account=input_dto.account,
                    target_date=input_dto.target_date,
                )
            )
        ).cache
        return RefreshScheduleUseCaseOutputDTO(fetched_at=cache.fetched_at)
