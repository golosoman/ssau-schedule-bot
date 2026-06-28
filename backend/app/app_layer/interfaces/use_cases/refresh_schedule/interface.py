from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.refresh_schedule.dto import (
    RefreshScheduleUseCaseInputDTO,
    RefreshScheduleUseCaseOutputDTO,
)


class IRefreshScheduleUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: RefreshScheduleUseCaseInputDTO,
    ) -> RefreshScheduleUseCaseOutputDTO:
        raise NotImplementedError
