from datetime import date

from app.domain.entities.lesson import Lesson
from app.domain.value_objects.subgroup import Subgroup


class DailyScheduleService:
    @staticmethod
    def filter_for_date(
        lessons: list[Lesson],
        target_date: date,
        week_number: int,
        subgroup: Subgroup,
    ) -> list[Lesson]:
        weekday = target_date.isoweekday()
        return [
            lesson
            for lesson in lessons
            if lesson.weekday == weekday
            and week_number in lesson.week_numbers
            and _lesson_matches_subgroup(lesson.subgroup, subgroup)
        ]


def _lesson_matches_subgroup(lesson_subgroup: int | None, subgroup: Subgroup) -> bool:
    if subgroup.is_all:
        return True
    if lesson_subgroup is None:
        return True
    return lesson_subgroup == subgroup.value
