from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from aiogram.types import Message

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.domain.entities.users import User
from app.domain.messages.info import InfoMessage
from app.domain.value_objects.timezone import Timezone


def command_args(message: Message) -> list[str]:
    if not message.text:
        return []
    return message.text.split()[1:]


def user_now(now_utc: datetime, timezone: Timezone) -> datetime:
    zone = timezone.tzinfo()
    return now_utc.astimezone(zone)


def build_status_message(user: User) -> InfoMessage:
    profile = user.ssau.profile
    group_label = str(profile.profile_ids.group_id) if profile is not None else "не определена"
    year_label = str(profile.profile_ids.year_id) if profile is not None else "не определен"
    subgroup_label = (
        str(profile.profile_details.subgroup) if profile is not None else "не определена"
    )
    creds = "есть" if user.ssau.credentials is not None else "нет"
    notify_status = "включены" if user.telegram.notify_enabled else "выключены"
    lines = [
        f"Группа: {group_label}",
        f"Год: {year_label}",
        f"Подгруппа: {subgroup_label}",
        f"Тип: {profile.profile_details.user_type if profile is not None else 'не определен'}",
        f"Уведомления: {notify_status}",
        f"Доступ: {creds}",
    ]
    return InfoMessage(title="Настройки", lines=lines)


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
