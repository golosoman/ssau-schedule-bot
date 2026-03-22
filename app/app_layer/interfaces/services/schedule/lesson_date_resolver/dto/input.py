from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson


class LessonDateResolverServiceInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    lesson: Lesson
    target_date: date
