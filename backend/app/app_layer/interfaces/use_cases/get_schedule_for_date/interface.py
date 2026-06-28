from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.get_schedule_for_date.dto import (
    GetScheduleForDateUseCaseInputDTO,
    GetScheduleForDateUseCaseOutputDTO,
)


class IGetScheduleForDateUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: GetScheduleForDateUseCaseInputDTO,
    ) -> GetScheduleForDateUseCaseOutputDTO:
        raise NotImplementedError
