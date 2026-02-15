from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable

from aiogram.types import Message

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.domain.entities.user import User
from app.domain.value_objects.timezone import Timezone


def command_args(message: Message) -> list[str]:
    if not message.text:
        return []
    return message.text.split()[1:]


def user_now(now_utc: datetime, timezone: Timezone) -> datetime:
    zone = timezone.tzinfo()
    return now_utc.astimezone(zone)


def format_lessons(lessons: list) -> str:
    if not lessons:
        return "Занятий нет."

    lines = []
    for lesson in sorted(lessons, key=lambda item: item.time.start):
        time_range = lesson.time.format_range()
        parts = [f"{time_range} {lesson.subject}"]
        if lesson.teacher:
            parts.append(lesson.teacher)
        if lesson.is_online and lesson.conference_url:
            parts.append(lesson.conference_url)
        lines.append(" | ".join(parts))

    return "\n".join(lines)


def format_next_lesson(start_at: datetime, lesson) -> str:
    time_label = start_at.strftime("%Y-%m-%d %H:%M")
    subject = lesson.subject
    teacher = lesson.teacher or "Преподаватель не указан"
    if lesson.is_online and lesson.conference_url:
        return (
            f"Следующая пара {time_label}: {subject} ({teacher})\n"
            f"{lesson.conference_url}"
        )
    return f"Следующая пара {time_label}: {subject} ({teacher})"


def format_status(user: User) -> str:
    profile = user.ssau.profile
    group_label = str(profile.group_id) if profile is not None else "не определена"
    year_label = str(profile.year_id) if profile is not None else "не определен"
    subgroup_label = str(profile.subgroup) if profile is not None else "не определена"
    creds = "есть" if user.ssau.credentials is not None else "нет"
    notify_status = "включены" if user.telegram.notify_enabled else "выключены"
    return (
        "Настройки:\n"
        f"- группа: {group_label}\n"
        f"- год: {year_label}\n"
        f"- подгруппа: {subgroup_label}\n"
        f"- тип: {profile.user_type if profile is not None else 'не определен'}\n"
        f"- уведомления: {notify_status}\n"
        f"- доступ: {creds}"
    )


def extract_telegram_identity(message: Message) -> str:
    fallback = f"user_{message.chat.id}"
    if not message.from_user:
        return fallback

    name_parts = [message.from_user.first_name, message.from_user.last_name]
    display_name = " ".join(part for part in name_parts if part)
    if not display_name:
        display_name = message.from_user.username or fallback
    return display_name


def credentials_missing(user: User) -> bool:
    return user.ssau.credentials is None


async def load_user(message: Message, use_case: RegisterUserUseCase) -> User:
    display_name = extract_telegram_identity(message)
    return await use_case.execute(message.chat.id, display_name)


async def ensure_profile(
    user: User,
    use_case: SyncUserProfileUseCase,
    *,
    force: bool = False,
) -> User:
    if credentials_missing(user):
        raise RuntimeError("Credentials are required to sync profile.")
    if not force and user.ssau.profile is not None:
        return user
    return await use_case.execute(user)


async def sync_cache(
    uow_factory: Callable[[], UnitOfWork],
    sync_service: ScheduleSyncService,
    user: User,
    target_date: datetime,
    *,
    max_age: timedelta | None = None,
    force: bool = False,
):
    async with uow_factory() as uow:
        if force or max_age is None:
            return await sync_service.sync_for_user(uow, user, target_date.date())
        return await sync_service.sync_if_stale(
            uow,
            user,
            target_date.date(),
            max_age,
        )
