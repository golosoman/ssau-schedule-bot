from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson
from app.domain.entities.user import User


class LessonNotification(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    user: User
    lesson: Lesson
    lesson_start: datetime
