from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime


class INotificationLogRepository(ABC):
    @abstractmethod
    async def was_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def mark_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: str,
        sent_at: datetime,
    ) -> None:
        raise NotImplementedError
