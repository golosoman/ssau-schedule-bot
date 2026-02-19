from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_layer.interfaces.repos.notification_log.interface import (
    NotificationLogRepository,
)
from app.domain.entities.notification_log import NotificationLog
from app.infra.db.models import NotificationLogModel


class SqlAlchemyNotificationLogRepository(NotificationLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def was_sent(self, user_id: int, lesson_id: int, lesson_date: date) -> bool:
        result = await self._session.execute(
            select(NotificationLogModel.id).where(
                NotificationLogModel.user_id == user_id,
                NotificationLogModel.lesson_id == lesson_id,
                NotificationLogModel.lesson_date == lesson_date,
            )
        )
        return result.scalar_one_or_none() is not None

    async def mark_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        sent_at: datetime,
    ) -> None:
        log = NotificationLog(
            user_id=user_id,
            lesson_id=lesson_id,
            lesson_date=lesson_date,
            sent_at=sent_at,
        )
        model = NotificationLogModel.from_domain_entity(log)
        self._session.add(model)
        await self._session.flush()
