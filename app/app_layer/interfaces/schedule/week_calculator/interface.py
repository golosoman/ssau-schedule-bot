from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

# Deprecated compatibility contract: prefer
# `app.app_layer.interfaces.services.schedule.week_calculator.interface`.


class IWeekCalculator(ABC):
    @abstractmethod
    def get_week_number(self, target_date: date) -> int:
        raise NotImplementedError
