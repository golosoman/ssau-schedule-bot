from datetime import date, datetime

from app.domain.entities.base import BaseEntity
from app.domain.value_objects.notification_type import NotificationType


class NotificationLogEntity(BaseEntity):
    """Журнал идемпотентности отправок (append-only, без ``updated_at``)."""

    account_id: int
    lesson_id: int
    lesson_date: date
    notification_type: NotificationType
    sent_at: datetime
