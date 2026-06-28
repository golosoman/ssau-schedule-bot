from abc import ABC, abstractmethod
from datetime import date, datetime

from app.domain.value_objects.notification_type import NotificationTypeEnum


class INotificationLogRepository(ABC):
    @abstractmethod
    async def was_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationTypeEnum,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def mark_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationTypeEnum,
        sent_at: datetime,
    ) -> None:
        raise NotImplementedError
