from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseEntity(BaseModel):
    """Базовый класс всех доменных сущностей: идентичность + аудит создания.

    Конвенция: доменные сущности иммутабельны и именуются с суффиксом ``Entity``.
    """

    model_config = ConfigDict(frozen=True)

    id: int
    created_at: datetime


class TimestampedEntity(BaseEntity):
    """Сущность, у которой таблица несёт ``updated_at`` (всё, кроме append-only журналов)."""

    updated_at: datetime
