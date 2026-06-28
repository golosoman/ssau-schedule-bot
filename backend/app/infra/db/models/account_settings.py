from sqlalchemy import BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import TimestampedTable


class AccountSettingsModel(TimestampedTable):
    __tablename__ = "account_settings"

    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    schedule_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
