from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.schedule.lesson_date_resolver.dto.input import (
    LessonDateResolverServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.lesson_date_resolver.dto.output import (
    LessonDateResolverServiceOutputDTO,
)


class ILessonDateResolverService(ABC):
    @abstractmethod
    def resolve_datetime(
        self,
        input_dto: LessonDateResolverServiceInputDTO,
    ) -> LessonDateResolverServiceOutputDTO:
        raise NotImplementedError
