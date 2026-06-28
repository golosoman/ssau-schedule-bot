from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.get_upcoming_lesson.dto import (
    GetUpcomingLessonUseCaseInputDTO,
    GetUpcomingLessonUseCaseOutputDTO,
)


class IGetUpcomingLessonUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: GetUpcomingLessonUseCaseInputDTO,
    ) -> GetUpcomingLessonUseCaseOutputDTO:
        raise NotImplementedError
