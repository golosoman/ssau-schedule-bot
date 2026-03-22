from app.app_layer.interfaces.services.schedule.daily_schedule.dto.input import (
    DailyScheduleServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.daily_schedule.dto.output import (
    DailyScheduleServiceOutputDTO,
)
from app.app_layer.interfaces.services.schedule.daily_schedule.interface import (
    IDailyScheduleService,
)
from app.domain.value_objects.subgroup import Subgroup


class DailyScheduleService(IDailyScheduleService):
    def filter_for_date(
        self,
        input_dto: DailyScheduleServiceInputDTO,
    ) -> DailyScheduleServiceOutputDTO:
        lessons = input_dto.lessons
        target_date = input_dto.target_date
        week_number = input_dto.week_number
        subgroup = input_dto.subgroup

        weekday = target_date.isoweekday()
        return DailyScheduleServiceOutputDTO(
            lessons=[
                lesson
                for lesson in lessons
                if lesson.weekday == weekday
                and week_number in lesson.week_numbers
                and _lesson_matches_subgroup(lesson.subgroup, subgroup)
            ]
        )


def _lesson_matches_subgroup(lesson_subgroup: int | None, subgroup: Subgroup) -> bool:
    if subgroup.is_all:
        return True
    if lesson_subgroup is None:
        return True
    return lesson_subgroup == subgroup.value
