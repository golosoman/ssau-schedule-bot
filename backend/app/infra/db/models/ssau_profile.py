from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import TimestampedTable


class SsauProfileModel(TimestampedTable):
    __tablename__ = "account_ssau_profiles"

    ssau_identity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("account_ssau_identities.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    year_id: Mapped[int] = mapped_column(Integer, nullable=False)
    group_name: Mapped[str] = mapped_column(String(128), nullable=False)
    academic_year_start: Mapped[date] = mapped_column(Date, nullable=False)
    subgroup: Mapped[str] = mapped_column(String(16), nullable=False)
    user_type: Mapped[str] = mapped_column(String(32), nullable=False)
