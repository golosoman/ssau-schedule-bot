from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.schedule.daily_schedule.dto import (
    DailyScheduleServiceInputDTO,
    DailyScheduleServiceOutputDTO,
)


class IDailyScheduleService(ABC):
    @abstractmethod
    def filter_for_date(
        self,
        input_dto: DailyScheduleServiceInputDTO,
    ) -> DailyScheduleServiceOutputDTO:
        raise NotImplementedError
