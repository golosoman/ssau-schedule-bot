from __future__ import annotations

from datetime import date, datetime, time, timezone
from types import SimpleNamespace

import pytest

from app.app_layer.interfaces.services.notifications.notification_planner.dto.input import (
    NotificationPlannerCollectDueInputDTO,
    NotificationPlannerMarkSentInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
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
        self._sent: set[tuple[int, int, date, str]] = set()

    async def was_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: str,
    ) -> bool:
        return (user_id, lesson_id, lesson_date, notification_type) in self._sent

    async def mark_sent(
        self,
        user_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: str,
        sent_at: datetime,
    ) -> None:
        self._sent.add((user_id, lesson_id, lesson_date, notification_type))


@pytest.mark.asyncio
async def test_collect_due_and_mark_sent() -> None:
    week_calculator = AcademicWeekCalculator()
    planner = NotificationPlanner(
        lead_minutes=15,
        timezone=Timezone(value="Europe/Samara"),
        week_calculator=week_calculator,
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
    week_number = week_calculator.get_week_number(
        WeekCalculatorServiceInputDTO(
            start_date=user.ssau.profile.profile_details.academic_year_start,
            target_date=now_local.date(),
        )
    ).week_number
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

    due = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(
                uow=uow,
                user=user,
                now=now_utc,
            )
        )
    ).notifications
    assert len(due) == 1
    assert due[0].notification_type == "before_start"

    await planner.mark_sent(
        NotificationPlannerMarkSentInputDTO(
            uow=uow,
            notification=due[0],
            sent_at=now_utc,
        )
    )
    due_again = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(
                uow=uow,
                user=user,
                now=now_utc,
            )
        )
    ).notifications
    assert due_again == []


@pytest.mark.asyncio
async def test_collect_due_sends_start_notification_once() -> None:
    week_calculator = AcademicWeekCalculator()
    planner = NotificationPlanner(
        lead_minutes=15,
        timezone=Timezone(value="Europe/Samara"),
        week_calculator=week_calculator,
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
    pre_start_utc = datetime(2025, 9, 1, 5, 50, tzinfo=timezone.utc)
    pre_start_local = pre_start_utc.astimezone(Timezone(value="Europe/Samara").tzinfo())
    week_number = week_calculator.get_week_number(
        WeekCalculatorServiceInputDTO(
            start_date=user.ssau.profile.profile_details.academic_year_start,
            target_date=pre_start_local.date(),
        )
    ).week_number
    lesson = Lesson(
        id=10,
        type="Лекция",
        subject="Math",
        teacher="Ivanov",
        weekday=pre_start_local.isoweekday(),
        week_numbers=[week_number],
        time=LessonTime(start=time(10, 0), end=time(11, 0)),
        is_online=False,
        conference_url=None,
        subgroup=None,
    )
    cache = ScheduleCache(
        user_id=1,
        week_number=week_number,
        fetched_at=pre_start_utc,
        lessons=[lesson],
    )
    uow = SimpleNamespace(
        schedule_cache=FakeScheduleCacheRepository(cache),
        notification_log=FakeNotificationLogRepository(),
    )

    before_start_due = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(
                uow=uow,
                user=user,
                now=pre_start_utc,
            )
        )
    ).notifications
    assert len(before_start_due) == 1
    assert before_start_due[0].notification_type == "before_start"
    await planner.mark_sent(
        NotificationPlannerMarkSentInputDTO(
            uow=uow,
            notification=before_start_due[0],
            sent_at=pre_start_utc,
        )
    )

    lesson_start_utc = datetime(2025, 9, 1, 6, 0, tzinfo=timezone.utc)
    at_start_due = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(
                uow=uow,
                user=user,
                now=lesson_start_utc,
            )
        )
    ).notifications
    assert len(at_start_due) == 1
    assert at_start_due[0].notification_type == "at_start"

    await planner.mark_sent(
        NotificationPlannerMarkSentInputDTO(
            uow=uow,
            notification=at_start_due[0],
            sent_at=lesson_start_utc,
        )
    )
    at_start_due_again = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(
                uow=uow,
                user=user,
                now=lesson_start_utc,
            )
        )
    ).notifications
    assert at_start_due_again == []
