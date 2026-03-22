from datetime import datetime

from app.app_layer.interfaces.services.schedule.lesson_date_resolver.dto.input import (
    LessonDateResolverServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.lesson_date_resolver.dto.output import (
    LessonDateResolverServiceOutputDTO,
)
from app.app_layer.interfaces.services.schedule.lesson_date_resolver.interface import (
    ILessonDateResolverService,
)


class LessonDateResolver(ILessonDateResolverService):
    def resolve_datetime(
        self,
        input_dto: LessonDateResolverServiceInputDTO,
    ) -> LessonDateResolverServiceOutputDTO:
        lesson = input_dto.lesson
        target_date = input_dto.target_date

        start_dt = datetime.combine(target_date, lesson.time.start)
        end_dt = datetime.combine(target_date, lesson.time.end)

        return LessonDateResolverServiceOutputDTO(
            start_datetime=start_dt,
            end_datetime=end_dt,
        )
