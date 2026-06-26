from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import (
    command_args,
    credentials_missing,
    ensure_profile,
    load_account,
    prompt_for_input,
)
from app.api.events.telegram.handlers.states import ArgPromptStates
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.use_cases.authenticate_user.dto import (
    AuthenticateUserUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.authenticate_user.enums import (
    AuthenticateUserStatusEnum,
)
from app.app_layer.interfaces.use_cases.authenticate_user.interface import (
    IAuthenticateUserUseCase,
)
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_settings.dto import (
    UpdateUserSettingsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.interface import (
    IUpdateUserSettingsUseCase,
)
from app.di.container import Container
from app.domain.constants import SubgroupValueEnum
from app.domain.messages.error import ErrorMessage
from app.domain.messages.info import InfoMessage
from app.domain.value_objects.subgroup import Subgroup
from app.logging.config import get_logger

logger = get_logger(__name__)

router = Router(name="profile")


_AUTH_PROMPT = "Отправь логин и пароль СГАУ через пробел:"
_AUTH_PLACEHOLDER = "ЛОГИН ПАРОЛЬ"
_SUBGROUP_PROMPT = "Какую подгруппу выбрать? Напиши 1, 2 или all:"
_SUBGROUP_PLACEHOLDER = "1 | 2 | all"


@router.message(Command("auth"))
@inject
async def handle_auth(
    message: Message,
    state: FSMContext,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    authenticate_use_case: IAuthenticateUserUseCase = Provide[
        Container.usecases.authenticate_user_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    args = command_args(message)
    if len(args) < 2:
        await state.set_state(ArgPromptStates.auth)
        await prompt_for_input(message, _AUTH_PROMPT, _AUTH_PLACEHOLDER)
        return
    await _process_auth(
        message, args[0], args[1], register_use_case, authenticate_use_case, notifier
    )


@router.message(ArgPromptStates.auth, F.text & ~F.text.startswith("/"))
@inject
async def handle_auth_reply(
    message: Message,
    state: FSMContext,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    authenticate_use_case: IAuthenticateUserUseCase = Provide[
        Container.usecases.authenticate_user_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2:
        await prompt_for_input(message, _AUTH_PROMPT, _AUTH_PLACEHOLDER)
        return
    await state.clear()
    await _process_auth(
        message, parts[0], parts[1], register_use_case, authenticate_use_case, notifier
    )


async def _process_auth(
    message: Message,
    login: str,
    password: str,
    register_use_case: IRegisterUserUseCase,
    authenticate_use_case: IAuthenticateUserUseCase,
    notifier: INotifier,
) -> None:
    await load_account(message, register_use_case)
    result = await authenticate_use_case.execute(
        AuthenticateUserUseCaseInputDTO(chat_id=message.chat.id, login=login, password=password)
    )

    if result.status is AuthenticateUserStatusEnum.PROFILE_FETCH_ERROR:
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Профиль не обновлен",
                details=["Данные сохранены, но профиль (группа/год) не получен."],
            ),
        )
        return

    profile = result.account.ssau_profile
    if result.status is AuthenticateUserStatusEnum.PROFILE_NOT_FOUND or profile is None:
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
                f"Группа: {profile.group_id.value}",
                f"Год: {profile.year_id.value}",
            ],
        ),
    )


@router.message(Command("subgroup"))
@inject
async def handle_subgroup(
    message: Message,
    state: FSMContext,
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
        await state.set_state(ArgPromptStates.subgroup)
        await prompt_for_input(message, _SUBGROUP_PROMPT, _SUBGROUP_PLACEHOLDER)
        return
    await _process_subgroup(
        message,
        args[0],
        register_use_case,
        update_settings_use_case,
        sync_profile_use_case,
        notifier,
    )


@router.message(ArgPromptStates.subgroup, F.text & ~F.text.startswith("/"))
@inject
async def handle_subgroup_reply(
    message: Message,
    state: FSMContext,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    update_settings_use_case: IUpdateUserSettingsUseCase = Provide[
        Container.usecases.update_user_settings_use_case
    ],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    await state.clear()
    parts = (message.text or "").split()
    await _process_subgroup(
        message,
        parts[0] if parts else "",
        register_use_case,
        update_settings_use_case,
        sync_profile_use_case,
        notifier,
    )


async def _process_subgroup(
    message: Message,
    raw_value: str,
    register_use_case: IRegisterUserUseCase,
    update_settings_use_case: IUpdateUserSettingsUseCase,
    sync_profile_use_case: ISyncUserProfileUseCase,
    notifier: INotifier,
) -> None:
    try:
        raw = raw_value.strip().lower()
        if raw == "all":
            subgroup = Subgroup.all()
        else:
            subgroup = Subgroup(value=SubgroupValueEnum(int(raw)))
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
