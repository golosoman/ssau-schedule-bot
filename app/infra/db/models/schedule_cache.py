from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.lesson import Lesson
from app.domain.entities.schedule_cache import ScheduleCache
from app.infra.db.base import BaseTable


class ScheduleCacheModel(BaseTable):
    __tablename__ = "schedule_cache"
    __table_args__ = (
        UniqueConstraint("user_id", "week_number", name="uq_schedule_cache_user_week"),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    lessons_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False)

    def to_domain_entity(self) -> ScheduleCache:
        lessons = [Lesson.model_validate(item) for item in self.lessons_json]

        return ScheduleCache(
            user_id=self.user_id,
            week_number=self.week_number,
            fetched_at=self._ensure_aware(self.fetched_at),
            lessons=lessons,
        )

    @classmethod
    def from_domain_entity(cls, cache: ScheduleCache) -> "ScheduleCacheModel":
        payload = [lesson.model_dump(mode="json") for lesson in cache.lessons]

        return cls(
            user_id=cache.user_id,
            week_number=cache.week_number,
            fetched_at=cache.fetched_at,
            lessons_json=payload,
        )

    def apply_domain_entity(self, cache: ScheduleCache) -> None:
        self.fetched_at = cache.fetched_at
        self.lessons_json = [lesson.model_dump(mode="json") for lesson in cache.lessons]

    @staticmethod
    def _ensure_aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
