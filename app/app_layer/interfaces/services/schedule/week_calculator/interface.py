from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.output import (
    WeekCalculatorServiceOutputDTO,
)


class IWeekCalculatorService(ABC):
    @abstractmethod
    def get_week_number(
        self,
        input_dto: WeekCalculatorServiceInputDTO,
    ) -> WeekCalculatorServiceOutputDTO:
        raise NotImplementedError
