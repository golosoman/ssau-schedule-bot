from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.lesson_time import LessonTime


class Lesson(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        ser_json_timedelta="iso8601",
    )

    id: int
    type: str
    subject: str
    teacher: str | None
    weekday: int
    week_numbers: list[int]
    time: LessonTime
    is_online: bool
    conference_url: str | None
    subgroup: int | None
