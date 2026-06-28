from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import TimestampedTable


class SsauIdentityModel(TimestampedTable):
    __tablename__ = "account_ssau_identities"

    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    login: Mapped[str] = mapped_column(String(64), nullable=False)
    encrypted_password: Mapped[str] = mapped_column(String(512), nullable=False)
