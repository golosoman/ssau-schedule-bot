from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.schedule.upcoming_lesson.dto.input import (
    UpcomingLessonServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.upcoming_lesson.dto.output import (
    UpcomingLessonServiceOutputDTO,
)


class IUpcomingLessonService(ABC):
    @abstractmethod
    def find_next(
        self,
        input_dto: UpcomingLessonServiceInputDTO,
    ) -> UpcomingLessonServiceOutputDTO:
        raise NotImplementedError
