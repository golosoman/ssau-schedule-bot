from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.schedule.daily_schedule.dto.input import (
    DailyScheduleServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.daily_schedule.dto.output import (
    DailyScheduleServiceOutputDTO,
)


class IDailyScheduleService(ABC):
    @abstractmethod
    def filter_for_date(
        self,
        input_dto: DailyScheduleServiceInputDTO,
    ) -> DailyScheduleServiceOutputDTO:
        raise NotImplementedError
