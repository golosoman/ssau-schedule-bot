from __future__ import annotations

from datetime import datetime

from app.domain.entities.lesson import Lesson
from app.domain.messages.base import TelegramMessage


class NotificationMessage(TelegramMessage):
    lesson: Lesson
    lesson_start: datetime
    title: str = "Напоминание"
