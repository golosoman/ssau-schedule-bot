from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import BaseTable


class NotificationLogModel(BaseTable):
    __tablename__ = "notification_log"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "lesson_id",
            "lesson_date",
            "notification_type",
            name="uq_notification_once",
        ),
    )

    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lesson_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(32), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
