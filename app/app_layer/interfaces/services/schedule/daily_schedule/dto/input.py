from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson
from app.domain.value_objects.subgroup import Subgroup


class DailyScheduleServiceInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    lessons: list[Lesson]
    target_date: date
    week_number: int
    subgroup: Subgroup
