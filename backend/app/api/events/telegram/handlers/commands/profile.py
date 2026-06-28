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
from app.app_layer.interfaces.security.state_token.interface import IStateTokenService
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
from app.settings.config import settings

logger = get_logger(__name__)

router = Router(name="profile")


_SUBGROUP_PROMPT = "Какую подгруппу выбрать? Напиши 1, 2 или all:"
_SUBGROUP_PLACEHOLDER = "1 | 2 | all"


@router.message(Command("auth"))
@inject
async def handle_auth(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    state_token_service: IStateTokenService = Provide[Container.core.state_token_service],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    # Аккаунт должен существовать — ручка авторизации ищет его по chat_id.
    await load_account(message, register_use_case)
    token = state_token_service.issue(message.chat.id)
    url = f"{settings.telegram.frontend_auth_url}?token={token}"
    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Вход через СНИУ",
            lines=[
                "Открой защищённую страницу и введи логин/пароль СНИУ там "
                "(ссылка действует ограниченное время):",
                url,
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
                details=["Сначала введи /auth и открой ссылку для входа через СНИУ."],
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
