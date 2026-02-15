from datetime import date

from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator


def test_week_number_start_date() -> None:
    calculator = AcademicWeekCalculator(date(2025, 9, 1))
    assert calculator.get_week_number(date(2025, 9, 1)) == 1


def test_week_number_next_week() -> None:
    calculator = AcademicWeekCalculator(date(2025, 9, 1))
    assert calculator.get_week_number(date(2025, 9, 8)) == 2


def test_week_number_before_start_returns_one() -> None:
    calculator = AcademicWeekCalculator(date(2025, 9, 1))
    assert calculator.get_week_number(date(2025, 8, 31)) == 1
