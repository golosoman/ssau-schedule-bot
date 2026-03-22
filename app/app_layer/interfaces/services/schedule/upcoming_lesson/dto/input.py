from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson
from app.domain.value_objects.subgroup import Subgroup


class UpcomingLessonServiceInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    lessons: list[Lesson]
    now_local: datetime
    week_number: int
    subgroup: Subgroup
