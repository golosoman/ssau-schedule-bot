from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.get_schedule.dto.input import GetScheduleUseCaseInputDTO
from app.app_layer.interfaces.use_cases.get_schedule.dto.output import GetScheduleUseCaseOutputDTO


class IGetScheduleUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: GetScheduleUseCaseInputDTO,
    ) -> GetScheduleUseCaseOutputDTO:
        raise NotImplementedError
