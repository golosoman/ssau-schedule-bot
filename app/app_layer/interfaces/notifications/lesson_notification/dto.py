from __future__ import annotations

from datetime import datetime
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson
from app.domain.entities.users import User

NotificationType: TypeAlias = Literal["before_start", "at_start"]


class LessonNotification(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    user: User
    lesson: Lesson
    lesson_start: datetime
    notification_type: NotificationType
