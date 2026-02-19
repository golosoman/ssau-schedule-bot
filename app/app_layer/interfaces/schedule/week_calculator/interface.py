from __future__ import annotations

from datetime import date
from typing import Protocol


class WeekCalculator(Protocol):
    def get_week_number(self, target_date: date) -> int: ...
