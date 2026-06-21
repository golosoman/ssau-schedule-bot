import asyncio
from datetime import UTC, date, datetime, time

import pytest

from app.app_layer.interfaces.cache.schedule.dto import CachedWeek
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.repos.account.dto import AccountView
from app.app_layer.interfaces.services.notifications.notification_planner.dto.input import (
    NotificationPlannerCollectDueInputDTO,
    NotificationPlannerMarkSentInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_service.dto.input import (
    NotificationServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.services.notifications.notification_planner import NotificationPlanner
from app.app_layer.services.notifications.notification_service import NotificationService
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.domain.constants import DEFAULT_SUBGROUP_VALUE
from app.domain.entities.account.account import AccountEntity
from app.domain.entities.account.account_settings import AccountSettingsEntity
from app.domain.entities.account.ssau_identity import SsauIdentityEntity
from app.domain.entities.account.ssau_profile import SsauProfileEntity
from app.domain.entities.account.telegram_identity import TelegramIdentityEntity
from app.domain.entities.lesson import Lesson
from app.domain.messages.base import TelegramMessage
from app.domain.messages.notification import NotificationMessage
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.lesson_time import LessonTime
from app.domain.value_objects.notification_type import NotificationType
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.timezone import Timezone
from app.domain.value_objects.year_id import YearId

_NOW = datetime(2025, 9, 1, tzinfo=UTC)


def _make_account(account_id: int = 1, chat_id: int = 111) -> AccountView:
    return AccountView(
        account=AccountEntity(id=account_id, created_at=_NOW, updated_at=_NOW),
        telegram=TelegramIdentityEntity(
            id=1, created_at=_NOW, updated_at=_NOW,
            account_id=account_id, chat_id=chat_id, display_name="tester",
        ),
        settings=AccountSettingsEntity(
            id=1, created_at=_NOW, updated_at=_NOW,
            account_id=account_id, schedule_notifications_enabled=True,
        ),
        ssau_identity=SsauIdentityEntity(
            id=1, created_at=_NOW, updated_at=_NOW,
            account_id=account_id, login="login", password="pass",
        ),
        ssau_profile=SsauProfileEntity(
            id=1, created_at=_NOW, updated_at=_NOW,
            ssau_identity_id=1,
            group_id=GroupId(value=755932538),
            year_id=YearId(value=14),
            group_name="Test",
            academic_year_start=date(2025, 9, 1),
            subgroup=Subgroup(value=DEFAULT_SUBGROUP_VALUE),
            user_type="student",
        ),
    )


class FakeScheduleCacheStore:
    def __init__(self) -> None:
        self._store: dict[tuple[int, int], CachedWeek] = {}

    async def get(self, account_id: int, week_number: int) -> CachedWeek | None:
        return self._store.get((account_id, week_number))

    async def set(self, account_id: int, week_number: int, week: CachedWeek) -> None:
        self._store[(account_id, week_number)] = week


class FakeNotificationLogRepository:
    def __init__(self) -> None:
        self._sent: set[tuple[int, int, date, NotificationType]] = set()

    async def was_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationType,
    ) -> bool:
        return (account_id, lesson_id, lesson_date, notification_type) in self._sent

    async def mark_sent(
        self,
        account_id: int,
        lesson_id: int,
        lesson_date: date,
        notification_type: NotificationType,
        sent_at: datetime,
    ) -> None:
        self._sent.add((account_id, lesson_id, lesson_date, notification_type))


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeNotifier(INotifier):
    def __init__(self) -> None:
        self.sent: list[tuple[int, TelegramMessage]] = []

    async def send(self, chat_id: int, message: TelegramMessage) -> None:
        self.sent.append((chat_id, message))


def _week_number(week_calculator: AcademicWeekCalculator, target: date) -> int:
    return week_calculator.get_week_number(
        WeekCalculatorServiceInputDTO(start_date=date(2025, 9, 1), target_date=target)
    ).week_number


def _build_planner(
    week_calculator: AcademicWeekCalculator,
    cache_store: FakeScheduleCacheStore,
    notification_log: FakeNotificationLogRepository,
) -> NotificationPlanner:
    return NotificationPlanner(
        lead_minutes=15,
        timezone=Timezone(value="Europe/Samara"),
        week_calculator=week_calculator,
        cache_store=cache_store,
        notification_log_repo=notification_log,
    )


def test_notification_service_sends_due_lesson_and_marks_it_sent() -> None:
    async def _run() -> None:
        week_calculator = AcademicWeekCalculator()
        cache_store = FakeScheduleCacheStore()
        notification_log = FakeNotificationLogRepository()
        planner = _build_planner(week_calculator, cache_store, notification_log)
        account = _make_account(chat_id=123456)

        now_utc = datetime(2025, 9, 1, 5, 50, tzinfo=UTC)
        now_local = now_utc.astimezone(Timezone(value="Europe/Samara").tzinfo())
        week_number = _week_number(week_calculator, now_local.date())
        lesson = Lesson(
            id=42,
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
        await cache_store.set(
            account.account_id,
            week_number,
            CachedWeek(fetched_at=now_utc, lessons=[lesson]),
        )

        notifier = FakeNotifier()
        service = NotificationService(
            planner=planner,
            notifier=notifier,
            clock=FakeClock(now_utc),
        )

        result = await service.process_user(NotificationServiceInputDTO(account=account))

        assert result.sent_count == 1
        assert len(notifier.sent) == 1
        chat_id, message = notifier.sent[0]
        assert chat_id == account.chat_id
        assert isinstance(message, NotificationMessage)
        assert message.title == "Напоминание"
        assert message.lesson.id == lesson.id
        assert message.lesson_start.date() == now_local.date()

        second_result = await service.process_user(NotificationServiceInputDTO(account=account))

        assert second_result.sent_count == 0
        assert len(notifier.sent) == 1

    asyncio.run(_run())


@pytest.mark.asyncio
async def test_collect_due_and_mark_sent() -> None:
    week_calculator = AcademicWeekCalculator()
    cache_store = FakeScheduleCacheStore()
    notification_log = FakeNotificationLogRepository()
    planner = _build_planner(week_calculator, cache_store, notification_log)
    account = _make_account()

    now_utc = datetime(2025, 9, 1, 5, 50, tzinfo=UTC)
    now_local = now_utc.astimezone(Timezone(value="Europe/Samara").tzinfo())
    week_number = _week_number(week_calculator, now_local.date())
    lesson = Lesson(
        id=10, type="Лекция", subject="Math", teacher="Ivanov",
        weekday=now_local.isoweekday(), week_numbers=[week_number],
        time=LessonTime(start=time(10, 0), end=time(11, 0)),
        is_online=False, conference_url=None, subgroup=None,
    )
    await cache_store.set(
        account.account_id, week_number, CachedWeek(fetched_at=now_utc, lessons=[lesson])
    )
    due = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(account=account, now=now_utc)
        )
    ).notifications
    assert len(due) == 1
    assert due[0].notification_type == NotificationType.BEFORE_START

    await planner.mark_sent(
        NotificationPlannerMarkSentInputDTO(notification=due[0], sent_at=now_utc)
    )
    due_again = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(account=account, now=now_utc)
        )
    ).notifications
    assert due_again == []


@pytest.mark.asyncio
async def test_collect_due_sends_start_notification_once() -> None:
    week_calculator = AcademicWeekCalculator()
    cache_store = FakeScheduleCacheStore()
    notification_log = FakeNotificationLogRepository()
    planner = _build_planner(week_calculator, cache_store, notification_log)
    account = _make_account()

    pre_start_utc = datetime(2025, 9, 1, 5, 50, tzinfo=UTC)
    pre_start_local = pre_start_utc.astimezone(Timezone(value="Europe/Samara").tzinfo())
    week_number = _week_number(week_calculator, pre_start_local.date())
    lesson = Lesson(
        id=10, type="Лекция", subject="Math", teacher="Ivanov",
        weekday=pre_start_local.isoweekday(), week_numbers=[week_number],
        time=LessonTime(start=time(10, 0), end=time(11, 0)),
        is_online=False, conference_url=None, subgroup=None,
    )
    await cache_store.set(
        account.account_id, week_number, CachedWeek(fetched_at=pre_start_utc, lessons=[lesson])
    )
    before_start_due = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(account=account, now=pre_start_utc)
        )
    ).notifications
    assert len(before_start_due) == 1
    assert before_start_due[0].notification_type == NotificationType.BEFORE_START
    await planner.mark_sent(
        NotificationPlannerMarkSentInputDTO(
            notification=before_start_due[0], sent_at=pre_start_utc
        )
    )

    lesson_start_utc = datetime(2025, 9, 1, 6, 0, tzinfo=UTC)
    at_start_due = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(account=account, now=lesson_start_utc)
        )
    ).notifications
    assert len(at_start_due) == 1
    assert at_start_due[0].notification_type == NotificationType.AT_START

    await planner.mark_sent(
        NotificationPlannerMarkSentInputDTO(
            notification=at_start_due[0], sent_at=lesson_start_utc
        )
    )
    at_start_due_again = (
        await planner.collect_due(
            NotificationPlannerCollectDueInputDTO(account=account, now=lesson_start_utc)
        )
    ).notifications
    assert at_start_due_again == []
