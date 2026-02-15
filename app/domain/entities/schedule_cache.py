from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson


class ScheduleCache(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    user_id: int
    week_number: int
    fetched_at: datetime
    lessons: list[Lesson]
