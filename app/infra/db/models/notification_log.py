from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.notification_log import NotificationLog
from app.infra.db.base import BaseTable


class NotificationLogModel(BaseTable):
    __tablename__ = "notification_log"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lesson_id",
            "lesson_date",
            name="uq_notification_once",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    lesson_id: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_domain_entity(self) -> NotificationLog:
        return NotificationLog(
            user_id=self.user_id,
            lesson_id=self.lesson_id,
            lesson_date=self.lesson_date,
            sent_at=self.sent_at,
        )

    @classmethod
    def from_domain_entity(cls, log: NotificationLog) -> "NotificationLogModel":
        return cls(
            user_id=log.user_id,
            lesson_id=log.lesson_id,
            lesson_date=log.lesson_date,
            sent_at=log.sent_at,
        )
