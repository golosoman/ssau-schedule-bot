from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson


class UpcomingLessonDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    lesson: Lesson
    start_at: datetime
