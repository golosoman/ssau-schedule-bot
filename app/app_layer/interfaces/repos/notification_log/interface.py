from __future__ import annotations

from typing import Protocol
from datetime import date, datetime


class NotificationLogRepository(Protocol):
    async def was_sent(self, user_id: int, lesson_id: int, lesson_date: date) -> bool:
        ...

    async def mark_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        sent_at: datetime,
    ) -> None:
        ...
