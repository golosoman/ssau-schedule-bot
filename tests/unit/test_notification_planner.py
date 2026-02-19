from __future__ import annotations

from datetime import date, datetime, time, timezone
from types import SimpleNamespace

import pytest

from app.app_layer.services.notifications.notification_planner import NotificationPlanner
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.domain.constants import DEFAULT_SUBGROUP_VALUE
from app.domain.entities.lesson import Lesson
from app.domain.entities.schedule_cache import ScheduleCache
from app.domain.entities.users import (
    SsauCredentials,
    SsauProfile,
    SsauProfileDetails,
    SsauProfileIds,
    SsauUser,
    TelegramUser,
    User,
)
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.year_id import YearId
from app.domain.value_objects.lesson_time import LessonTime
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.timezone import Timezone


class FakeScheduleCacheRepository:
    def __init__(self, cache: ScheduleCache | None) -> None:
        self._cache = cache

    async def get(self, user_id: int, week_number: int) -> ScheduleCache | None:
        if self._cache is None:
            return None
        if self._cache.user_id != user_id or self._cache.week_number != week_number:
            return None
        return self._cache


class FakeNotificationLogRepository:
    def __init__(self) -> None:
        self._sent: set[tuple[int, int, date]] = set()

    async def was_sent(self, user_id: int, lesson_id: int, lesson_date: date) -> bool:
        return (user_id, lesson_id, lesson_date) in self._sent

    async def mark_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        sent_at: datetime,
    ) -> None:
        self._sent.add((user_id, lesson_id, lesson_date))


@pytest.mark.asyncio
async def test_collect_due_and_mark_sent() -> None:
    planner = NotificationPlanner(
        lead_minutes=15,
        timezone=Timezone(value="Europe/Samara"),
    )
    user = User(
        id=1,
        telegram=TelegramUser(
            chat_id=111,
            display_name="tester",
            notify_enabled=True,
        ),
        ssau=SsauUser(
            credentials=SsauCredentials(login="login", password="pass"),
            profile=SsauProfile(
                profile_ids=SsauProfileIds(
                    group_id=GroupId(value=755932538),
                    year_id=YearId(value=14),
                ),
                profile_details=SsauProfileDetails(
                    group_name="Test",
                    academic_year_start=date(2025, 9, 1),
                    subgroup=Subgroup(value=DEFAULT_SUBGROUP_VALUE),
                    user_type="student",
                ),
            ),
        ),
    )
    now_utc = datetime(2025, 9, 1, 5, 50, tzinfo=timezone.utc)
    now_local = now_utc.astimezone(Timezone(value="Europe/Samara").tzinfo())
    week_number = AcademicWeekCalculator(
        user.ssau.profile.profile_details.academic_year_start
    ).get_week_number(now_local.date())
    lesson = Lesson(
        id=10,
        type="Лекция",
        subject="Math",
        teacher="Ivanov",
        weekday=now_local.isoweekday(),
        week_numbers=[week_number],
        time=LessonTime(start=time(10, 0), end=time(11, 0)),
        is_online=False,
        conference_url=None,
        subgroup=None,
    )
    cache = ScheduleCache(
        user_id=1,
        week_number=week_number,
        fetched_at=now_utc,
        lessons=[lesson],
    )
    uow = SimpleNamespace(
        schedule_cache=FakeScheduleCacheRepository(cache),
        notification_log=FakeNotificationLogRepository(),
    )

    due = await planner.collect_due(uow, user, now_utc)
    assert len(due) == 1

    await planner.mark_sent(uow, due[0], sent_at=now_utc)
    due_again = await planner.collect_due(uow, user, now_utc)
    assert due_again == []
