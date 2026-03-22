from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson


class GetScheduleUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    lessons: list[Lesson]
