from datetime import datetime

from aiogram.types import ForceReply, Message

from app.app_layer.interfaces.cache.schedule.dto import CachedWeekDTO
from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.app_layer.interfaces.services.schedule.schedule_sync.dto import (
    ScheduleSyncForUserInputDTO,
    ScheduleSyncIfStaleInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.use_cases.register_user.dto import (
    RegisterUserUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.dto import (
    SyncUserProfileUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.domain.messages.info import InfoMessage
from app.domain.value_objects.timezone import Timezone


def command_args(message: Message) -> list[str]:
    if not message.text:
        return []
    return message.text.split()[1:]


async def prompt_for_input(message: Message, text: str, placeholder: str) -> None:
    """ForceReply-промпт: фокусирует поле ввода с подсказкой-плейсхолдером.

    Используется для команд с аргументами — чтобы пользователь дописал значение
    вместо мгновенной отправки голой команды.
    """
    await message.answer(text, reply_markup=ForceReply(input_field_placeholder=placeholder))


def user_now(now_utc: datetime, timezone: Timezone) -> datetime:
    zone = timezone.tzinfo()
    return now_utc.astimezone(zone)


def build_status_message(account: AccountViewDTO) -> InfoMessage:
    profile = account.ssau_profile
    group_label = profile.group_name if profile is not None else "не определена"
    subgroup_label = str(profile.subgroup) if profile is not None else "не определена"
    user_type_label = profile.user_type if profile is not None else "не определен"
    creds = "есть" if account.is_authed else "нет"
    notify_status = "включены" if account.settings.schedule_notifications_enabled else "выключены"
    lines = [
        f"Группа: {group_label}",
        f"Подгруппа: {subgroup_label}",
        f"Тип: {user_type_label}",
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


def credentials_missing(account: AccountViewDTO) -> bool:
    return not account.is_authed


async def load_account(message: Message, use_case: IRegisterUserUseCase) -> AccountViewDTO:
    display_name = extract_telegram_identity(message)
    return (
        await use_case.execute(
            RegisterUserUseCaseInputDTO(
                chat_id=message.chat.id,
                display_name=display_name,
            )
        )
    ).account


async def ensure_profile(
    account: AccountViewDTO,
    use_case: ISyncUserProfileUseCase,
    *,
    force: bool = False,
) -> AccountViewDTO:
    if not account.is_authed:
        raise RuntimeError("Credentials are required to sync profile.")
    if not force and account.is_provisioned:
        return account
    return (await use_case.execute(SyncUserProfileUseCaseInputDTO(account=account))).account


async def sync_cache(
    sync_service: IScheduleSyncService,
    account: AccountViewDTO,
    target_date: datetime,
    *,
    force: bool = False,
) -> CachedWeekDTO:
    if force:
        return (
            await sync_service.sync_for_user(
                ScheduleSyncForUserInputDTO(account=account, target_date=target_date.date())
            )
        ).cache
    return (
        await sync_service.sync_if_stale(
            ScheduleSyncIfStaleInputDTO(account=account, target_date=target_date.date())
        )
    ).cache
