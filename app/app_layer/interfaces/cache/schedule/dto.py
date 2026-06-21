from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.lesson import Lesson


class CachedWeek(BaseModel):
    """Значение кэша расписания на неделю (хранится в Valkey под TTL)."""

    model_config = ConfigDict(frozen=True)

    fetched_at: datetime
    lessons: list[Lesson]
