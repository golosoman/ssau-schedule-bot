from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.app_layer.interfaces.notifications.lesson_notification.dto import (
    LessonNotification,
    NotificationType,
)
from app.app_layer.interfaces.services.notifications.notification_planner.dto.input import (
    NotificationPlannerCollectDueInputDTO,
    NotificationPlannerMarkSentInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_planner.dto.output import (
    NotificationPlannerCollectDueOutputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_planner.interface import (
    INotificationPlannerService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.timezone import Timezone

BEFORE_START_NOTIFICATION_TYPE: NotificationType = "before_start"
AT_START_NOTIFICATION_TYPE: NotificationType = "at_start"


class NotificationPlanner(INotificationPlannerService):
    def __init__(
        self,
        lead_minutes: int,
        timezone: Timezone,
        week_calculator: IWeekCalculatorService,
    ) -> None:
        self._lead_minutes = lead_minutes
        self._timezone = timezone
        self._week_calculator = week_calculator

    async def collect_due(
        self,
        input_dto: NotificationPlannerCollectDueInputDTO,
    ) -> NotificationPlannerCollectDueOutputDTO:
        uow = input_dto.uow
        user = input_dto.user
        now = input_dto.now

        if user.id is None:
            return NotificationPlannerCollectDueOutputDTO(notifications=[])
        if user.ssau.profile is None:
            return NotificationPlannerCollectDueOutputDTO(notifications=[])

        now_local = self._to_local_time(now)
        week_number = self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=user.ssau.profile.profile_details.academic_year_start,
                target_date=now_local.date(),
            )
        ).week_number
        cache = await uow.schedule_cache.get(user.id, week_number)
        if cache is None:
            return NotificationPlannerCollectDueOutputDTO(notifications=[])

        due: list[LessonNotification] = []
        today = now_local.date()
        for lesson in cache.lessons:
            if lesson.weekday != now_local.isoweekday():
                continue
            if week_number not in lesson.week_numbers:
                continue
            if not _lesson_matches_subgroup(
                lesson.subgroup,
                user.ssau.profile.profile_details.subgroup,
            ):
                continue

            lesson_start = datetime.combine(
                today,
                lesson.time.start,
                tzinfo=now_local.tzinfo,
            )
            lesson_end = datetime.combine(
                today,
                lesson.time.end,
                tzinfo=now_local.tzinfo,
            )
            notification_type = _resolve_notification_type(
                now=now_local,
                lesson_start=lesson_start,
                lesson_end=lesson_end,
                lead_minutes=self._lead_minutes,
            )
            if notification_type is None:
                continue

            already_sent = await uow.notification_log.was_sent(
                user.id,
                lesson.id,
                today,
                notification_type,
            )
            if already_sent:
                continue

            due.append(
                LessonNotification(
                    user=user,
                    lesson=lesson,
                    lesson_start=lesson_start,
                    notification_type=notification_type,
                )
            )

        return NotificationPlannerCollectDueOutputDTO(notifications=due)

    async def mark_sent(
        self,
        input_dto: NotificationPlannerMarkSentInputDTO,
    ) -> None:
        uow = input_dto.uow
        notification = input_dto.notification
        if notification.user.id is None:
            return
        sent_at = input_dto.sent_at or datetime.now(timezone.utc)
        await uow.notification_log.mark_sent(
            user_id=notification.user.id,
            lesson_id=notification.lesson.id,
            lesson_date=notification.lesson_start.date(),
            notification_type=notification.notification_type,
            sent_at=sent_at,
        )

    def _to_local_time(self, now: datetime) -> datetime:
        zone = self._timezone.tzinfo()
        if now.tzinfo is None:
            return now.replace(tzinfo=zone)
        return now.astimezone(zone)


def _lesson_matches_subgroup(lesson_subgroup: int | None, subgroup: Subgroup) -> bool:
    if subgroup.is_all:
        return True
    if lesson_subgroup is None:
        return True
    return lesson_subgroup == subgroup.value


def _resolve_notification_type(
    now: datetime,
    lesson_start: datetime,
    lesson_end: datetime,
    lead_minutes: int,
) -> NotificationType | None:
    notify_time = lesson_start - timedelta(minutes=lead_minutes)
    if notify_time <= now < lesson_start:
        return BEFORE_START_NOTIFICATION_TYPE
    if lesson_start <= now < lesson_end:
        return AT_START_NOTIFICATION_TYPE
    return None
