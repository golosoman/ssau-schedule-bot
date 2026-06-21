from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import (
    command_args,
    credentials_missing,
    ensure_profile,
    load_account,
)
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.dto.input import (
    UpdateUserCredentialsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.interface import (
    IUpdateUserCredentialsUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_settings.dto.input import (
    UpdateUserSettingsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.interface import (
    IUpdateUserSettingsUseCase,
)
from app.di.container import Container
from app.domain.constants import SubgroupValue
from app.domain.messages.error import ErrorMessage
from app.domain.messages.info import InfoMessage
from app.domain.value_objects.subgroup import Subgroup
from app.logging.config import get_logger

logger = get_logger(__name__)

router = Router(name="profile")


@router.message(Command("auth"))
@inject
async def handle_auth(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    update_credentials_use_case: IUpdateUserCredentialsUseCase = Provide[
        Container.usecases.update_user_credentials_use_case
    ],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    args = command_args(message)
    if len(args) < 2:
        await notifier.send(
            message.chat.id,
            InfoMessage(title="Использование", lines=["/auth ЛОГИН ПАРОЛЬ"]),
        )
        return

    login, password = args[0], args[1]
    await load_account(message, register_use_case)
    account = (
        await update_credentials_use_case.execute(
            UpdateUserCredentialsUseCaseInputDTO(
                chat_id=message.chat.id,
                login=login,
                password=password,
            )
        )
    ).account

    try:
        account = await ensure_profile(account, sync_profile_use_case, force=True)
    except Exception:
        logger.exception("Profile sync failed for user %s.", message.chat.id)
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Профиль не обновлен",
                details=["Данные сохранены, но профиль (группа/год) не получен."],
            ),
        )
        return

    if account.ssau_profile is None:
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Профиль не получен",
                details=["Данные сохранены, но профиль (группа/год) не найден."],
            ),
        )
        return
    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Данные сохранены",
            lines=[
                f"Группа: {account.ssau_profile.group_id.value}",
                f"Год: {account.ssau_profile.year_id.value}",
            ],
        ),
    )


@router.message(Command("subgroup"))
@inject
async def handle_subgroup(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    update_settings_use_case: IUpdateUserSettingsUseCase = Provide[
        Container.usecases.update_user_settings_use_case
    ],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    args = command_args(message)
    if not args:
        await notifier.send(
            message.chat.id,
            InfoMessage(title="Использование", lines=["/subgroup 1|2|all"]),
        )
        return

    try:
        raw = args[0].strip().lower()
        if raw == "all":
            subgroup = Subgroup.all()
        else:
            subgroup = Subgroup(value=SubgroupValue(int(raw)))
    except (ValueError, TypeError):
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Неверное значение",
                details=["Подгруппа должна быть 1, 2 или all."],
            ),
        )
        return

    account = await load_account(message, register_use_case)
    if credentials_missing(account):
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Нет доступа",
                details=["Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ"],
            ),
        )
        return
    try:
        await ensure_profile(account, sync_profile_use_case)
    except Exception:
        logger.exception("Profile sync failed for user %s.", message.chat.id)
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Профиль не получен", details=["Не удалось получить профиль."]),
        )
        return
    await update_settings_use_case.execute(
        UpdateUserSettingsUseCaseInputDTO(
            chat_id=message.chat.id,
            subgroup=subgroup,
        )
    )
    await notifier.send(
        message.chat.id,
        InfoMessage(title="Подгруппа обновлена", lines=[f"Текущая подгруппа: {subgroup}."]),
    )
