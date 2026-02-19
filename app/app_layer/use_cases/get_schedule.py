from datetime import date

from app.app_layer.interfaces.http.ssau.interface import ScheduleRepository
from app.app_layer.interfaces.schedule.week_calculator.interface import WeekCalculator
from app.domain.entities.lesson import Lesson


class GetScheduleUseCase:
    def __init__(
        self,
        repository: ScheduleRepository,
        week_calculator: WeekCalculator,
    ):
        self._repository = repository
        self._week_calculator = week_calculator

    async def execute(self, target_date: date) -> list[Lesson]:

        week_number = self._week_calculator.get_week_number(target_date)
        weekday = target_date.isoweekday()

        lessons = await self._repository.get_schedule(week_number)

        return [
            lesson
            for lesson in lessons
            if week_number in lesson.week_numbers and lesson.weekday == weekday
        ]
