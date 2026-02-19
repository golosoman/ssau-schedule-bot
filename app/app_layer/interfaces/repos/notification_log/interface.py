from __future__ import annotations

from datetime import date, datetime
from typing import Protocol


class NotificationLogRepository(Protocol):
    async def was_sent(self, user_id: int, lesson_id: int, lesson_date: date) -> bool: ...

    async def mark_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        sent_at: datetime,
    ) -> None: ...
