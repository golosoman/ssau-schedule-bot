from abc import ABC, abstractmethod
from datetime import date, datetime

from app.domain.value_objects.notification_type import NotificationType


class INotificationLogRepository(ABC):
    @abstractmethod
    async def was_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationType,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def mark_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationType,
        sent_at: datetime,
    ) -> None:
        raise NotImplementedError
