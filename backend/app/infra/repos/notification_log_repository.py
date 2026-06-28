from datetime import date, datetime

from sqlalchemy import select

from app.app_layer.interfaces.repos.notification_log.interface import (
    INotificationLogRepository,
)
from app.domain.value_objects.notification_type import NotificationTypeEnum
from app.infra.db.models import NotificationLogModel
from app.infra.repos.base import BaseSqlAlchemyRepository


class SqlAlchemyNotificationLogRepository(BaseSqlAlchemyRepository, INotificationLogRepository):
    async def was_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationTypeEnum,
    ) -> bool:
        result = await self._session.execute(
            select(NotificationLogModel.id).where(
                NotificationLogModel.account_id == account_id,
                NotificationLogModel.lesson_id == lesson_id,
                NotificationLogModel.lesson_date == lesson_date,
                NotificationLogModel.notification_type == notification_type.value,
            )
        )
        return result.scalar_one_or_none() is not None

    async def mark_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationTypeEnum,
        sent_at: datetime,
    ) -> None:
        model = NotificationLogModel(
            account_id=account_id,
            lesson_id=lesson_id,
            lesson_date=lesson_date,
            notification_type=notification_type.value,
            sent_at=sent_at,
        )
        self._session.add(model)
        await self._session.flush()
