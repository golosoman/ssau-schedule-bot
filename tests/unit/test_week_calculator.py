from datetime import date

from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator


def test_week_number_start_date() -> None:
    calculator = AcademicWeekCalculator()
    assert (
        calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=date(2025, 9, 1),
                target_date=date(2025, 9, 1),
            )
        ).week_number
        == 1
    )


def test_week_number_next_week() -> None:
    calculator = AcademicWeekCalculator()
    assert (
        calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=date(2025, 9, 1),
                target_date=date(2025, 9, 8),
            )
        ).week_number
        == 2
    )


def test_week_number_before_start_returns_one() -> None:
    calculator = AcademicWeekCalculator()
    assert (
        calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=date(2025, 9, 1),
                target_date=date(2025, 8, 31),
            )
        ).week_number
        == 1
    )
