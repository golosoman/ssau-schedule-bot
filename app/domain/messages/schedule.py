from __future__ import annotations

from datetime import date

from app.domain.entities.lesson import Lesson
from app.domain.messages.base import TelegramMessage


class ScheduleMessage(TelegramMessage):
    date: date
    lessons: list[Lesson]
    title: str = "Расписание"
