import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import command_args, ensure_profile, load_user
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.app_layer.use_cases.update_user_credentials import UpdateUserCredentialsUseCase
from app.app_layer.use_cases.update_user_settings import UpdateUserSettingsUseCase
from app.di import Container
from app.domain.value_objects.subgroup import Subgroup

logger = logging.getLogger(__name__)

router = Router(name="profile")


@router.message(Command("auth"))
@inject
async def handle_auth(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
    update_credentials_use_case: UpdateUserCredentialsUseCase = Provide[
        Container.update_user_credentials_use_case
    ],
    sync_profile_use_case: SyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
) -> None:
    args = command_args(message)
    if len(args) < 2:
        await message.answer("Использование: /auth ЛОГИН ПАРОЛЬ")
        return

    login, password = args[0], args[1]
    await load_user(message, register_use_case)
    user = await update_credentials_use_case.execute(message.chat.id, login, password)

    try:
        user = await ensure_profile(user, sync_profile_use_case, force=True)
    except Exception:
        logger.exception("Profile sync failed for user %s.", message.chat.id)
        await message.answer(
            "Данные сохранены, но не удалось обновить профиль (группа/год)."
        )
        return

    if user.ssau.profile is None:
        await message.answer(
            "Данные сохранены, но профиль не получен (группа/год)."
        )
        return
    await message.answer(
        f"Данные сохранены. Профиль: группа {user.ssau.profile.group_id}, "
        f"год {user.ssau.profile.year_id}."
    )


@router.message(Command("subgroup"))
@inject
async def handle_subgroup(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
    update_settings_use_case: UpdateUserSettingsUseCase = Provide[
        Container.update_user_settings_use_case
    ],
    sync_profile_use_case: SyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
) -> None:
    args = command_args(message)
    if not args:
        await message.answer("Использование: /subgroup 1|2")
        return

    try:
        subgroup = Subgroup(value=int(args[0]))
    except ValueError:
        await message.answer("Подгруппа должна быть 1 или 2.")
        return

    user = await load_user(message, register_use_case)
    if user.ssau.credentials is None:
        await message.answer("Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ")
        return
    try:
        user = await ensure_profile(user, sync_profile_use_case)
    except Exception:
        logger.exception("Profile sync failed for user %s.", message.chat.id)
        await message.answer("Не удалось получить профиль (группа/год).")
        return
    await update_settings_use_case.execute(message.chat.id, subgroup=subgroup)
    await message.answer(f"Подгруппа установлена: {subgroup}.")
