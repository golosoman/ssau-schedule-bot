from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import TimestampedTable


class TelegramIdentityModel(TimestampedTable):
    __tablename__ = "account_telegram_identities"

    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    telegram_chat_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    telegram_display_name: Mapped[str] = mapped_column(String(128), nullable=False)
