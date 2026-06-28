from app.app_layer.interfaces.services.schedule.week_calculator.dto import (
    WeekCalculatorServiceInputDTO,
    WeekCalculatorServiceOutputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.logging.config import get_logger

logger = get_logger(__name__)


class AcademicWeekCalculator(IWeekCalculatorService):
    def get_week_number(
        self,
        input_dto: WeekCalculatorServiceInputDTO,
    ) -> WeekCalculatorServiceOutputDTO:
        start_date = input_dto.start_date
        target_date = input_dto.target_date
        delta_days = (target_date - start_date).days
        if delta_days < 0:
            logger.warning(
                "Target date %s is before academic year start %s.",
                target_date,
                start_date,
            )
            return WeekCalculatorServiceOutputDTO(week_number=1)
        week_number = delta_days // 7 + 1
        logger.debug(
            "Academic week %s for %s (start %s, delta %s days).",
            week_number,
            target_date,
            start_date,
            delta_days,
        )
        return WeekCalculatorServiceOutputDTO(week_number=week_number)
