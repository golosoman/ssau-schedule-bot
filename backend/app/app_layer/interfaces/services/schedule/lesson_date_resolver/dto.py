from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson


class LessonDateResolverServiceInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    lesson: Lesson
    target_date: date


class LessonDateResolverServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    start_datetime: datetime
    end_datetime: datetime
