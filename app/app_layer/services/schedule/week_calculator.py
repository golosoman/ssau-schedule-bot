from __future__ import annotations

import logging
from datetime import date

logger = logging.getLogger(__name__)


class AcademicWeekCalculator:
    def __init__(self, start_date: date):
        self._start_date = start_date

    def get_week_number(self, target_date: date) -> int:
        delta_days = (target_date - self._start_date).days
        if delta_days < 0:
            logger.warning(
                "Target date %s is before academic year start %s.",
                target_date,
                self._start_date,
            )
            return 1
        week_number = delta_days // 7 + 1
        logger.debug(
            "Academic week %s for %s (start %s, delta %s days).",
            week_number,
            target_date,
            self._start_date,
            delta_days,
        )
        return week_number
