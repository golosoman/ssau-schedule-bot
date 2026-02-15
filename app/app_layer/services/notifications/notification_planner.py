from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.interfaces.notifications.lesson_notification.dto import (
    LessonNotification,
)
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.domain.entities.user import User
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.timezone import Timezone


class NotificationPlanner:

    def __init__(self, lead_minutes: int, timezone: Timezone) -> None:
        self._lead_minutes = lead_minutes
        self._timezone = timezone

    async def collect_due(
        self,
        uow: UnitOfWork,
        user: User,
        now: datetime,
    ) -> list[LessonNotification]:
        if user.id is None:
            return []
        if user.ssau.profile is None:
            return []

        now_local = self._to_local_time(now)
        week_number = AcademicWeekCalculator(
            user.ssau.profile.academic_year_start
        ).get_week_number(now_local.date())
        cache = await uow.schedule_cache.get(user.id, week_number)
        if cache is None:
            return []

        due: list[LessonNotification] = []
        today = now_local.date()
        for lesson in cache.lessons:
            if lesson.weekday != now_local.isoweekday():
                continue
            if week_number not in lesson.week_numbers:
                continue
            if not _lesson_matches_subgroup(
                lesson.subgroup,
                user.ssau.profile.subgroup,
            ):
                continue

            lesson_start = datetime.combine(
                today,
                lesson.time.start,
                tzinfo=now_local.tzinfo,
            )
            notify_time = lesson_start - timedelta(minutes=self._lead_minutes)
            if not (notify_time <= now_local < lesson_start):
                continue

            already_sent = await uow.notification_log.was_sent(
                user.id,
                lesson.id,
                today,
            )
            if already_sent:
                continue

            due.append(
                LessonNotification(
                    user=user,
                    lesson=lesson,
                    lesson_start=lesson_start,
                )
            )

        return due

    async def mark_sent(
        self,
        uow: UnitOfWork,
        notification: LessonNotification,
        sent_at: datetime | None = None,
    ) -> None:
        if notification.user.id is None:
            return
        sent_at = sent_at or datetime.now(timezone.utc)
        await uow.notification_log.mark_sent(
            user_id=notification.user.id,
            lesson_id=notification.lesson.id,
            lesson_date=notification.lesson_start.date(),
            sent_at=sent_at,
        )

    def _to_local_time(self, now: datetime) -> datetime:
        zone = self._timezone.tzinfo()
        if now.tzinfo is None:
            return now.replace(tzinfo=zone)
        return now.astimezone(zone)


def _lesson_matches_subgroup(lesson_subgroup: int | None, subgroup: Subgroup) -> bool:
    if lesson_subgroup is None:
        return True
    return lesson_subgroup == subgroup.value
