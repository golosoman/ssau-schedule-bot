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
    user_now,
)
from app.api.events.telegram.handlers.states import ArgPromptStates
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.time.clock.interface import IClock
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.dto import (
    GetUpcomingLessonUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.interface import (
    IGetUpcomingLessonUseCase,
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
from app.domain.messages.error import ErrorMessage
from app.domain.messages.info import InfoMessage
from app.domain.messages.notification import NotificationMessage
from app.domain.value_objects.timezone import Timezone
from app.logging.config import get_logger

logger = get_logger(__name__)

router = Router(name="notifications")

_NOTIFY_PROMPT = "Включить или выключить уведомления? Напиши on или off:"
_NOTIFY_PLACEHOLDER = "on | off"


@router.message(Command("notify"))
@inject
async def handle_notify(
    message: Message,
    state: FSMContext,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    update_settings_use_case: IUpdateUserSettingsUseCase = Provide[
        Container.usecases.update_user_settings_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    args = command_args(message)
    if not args:
        await state.set_state(ArgPromptStates.notify)
        await prompt_for_input(message, _NOTIFY_PROMPT, _NOTIFY_PLACEHOLDER)
        return
    await _process_notify(message, args[0], register_use_case, update_settings_use_case, notifier)


@router.message(ArgPromptStates.notify, F.text & ~F.text.startswith("/"))
@inject
async def handle_notify_reply(
    message: Message,
    state: FSMContext,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    update_settings_use_case: IUpdateUserSettingsUseCase = Provide[
        Container.usecases.update_user_settings_use_case
    ],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
    await state.clear()
    parts = (message.text or "").split()
    await _process_notify(
        message, parts[0] if parts else "", register_use_case, update_settings_use_case, notifier
    )


async def _process_notify(
    message: Message,
    arg: str,
    register_use_case: IRegisterUserUseCase,
    update_settings_use_case: IUpdateUserSettingsUseCase,
    notifier: INotifier,
) -> None:
    if arg.strip().lower() not in {"on", "off"}:
        await notifier.send(
            message.chat.id,
            InfoMessage(title="Использование", lines=["/notify on|off"]),
        )
        return

    enabled = arg.strip().lower() == "on"
    await load_account(message, register_use_case)
    await update_settings_use_case.execute(
        UpdateUserSettingsUseCaseInputDTO(
            chat_id=message.chat.id,
            notify_enabled=enabled,
        )
    )

    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Уведомления",
            lines=[f"{'Включены' if enabled else 'Выключены'}."],
        ),
    )


@router.message(Command("notify_test"))
@inject
async def handle_notify_test(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    get_upcoming_lesson_use_case: IGetUpcomingLessonUseCase = Provide[
        Container.usecases.get_upcoming_lesson_use_case
    ],
    clock: IClock = Provide[Container.core.clock],
    timezone: Timezone = Provide[Container.core.default_timezone],
    notifier: INotifier = Provide[Container.telegram.notifier],
) -> None:
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
        account = await ensure_profile(account, sync_profile_use_case)
        now_local = user_now(clock.now(), timezone)
    except ValueError:
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Некорректная таймзона", details=["Сообщи администратору."]),
        )
        return
    except Exception:
        logger.exception("Profile sync failed for user %s.", message.chat.id)
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Профиль не получен",
                details=["Не удалось получить данные профиля (группа/год)."],
            ),
        )
        return

    if account.ssau_profile is None:
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Профиль не получен", details=["Не удалось получить профиль."]),
        )
        return

    next_lesson = (
        await get_upcoming_lesson_use_case.execute(
            GetUpcomingLessonUseCaseInputDTO(account=account, now_local=now_local)
        )
    ).upcoming_lesson

    if next_lesson is None:
        await notifier.send(
            message.chat.id,
            InfoMessage(title="Тест уведомления", lines=["Ближайших занятий не найдено."]),
        )
        return

    await notifier.send(
        message.chat.id,
        NotificationMessage(
            title="Тест уведомления",
            lesson=next_lesson.lesson,
            lesson_start=next_lesson.start_at,
        ),
    )
