from datetime import timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import (
    credentials_missing,
    ensure_profile,
    load_account,
    user_now,
)
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.telegram.renderer.interface import ITelegramMessageRenderer
from app.app_layer.interfaces.telegram.sender.dto import (
    TelegramInlineKeyboardButtonDTO,
    TelegramReplyMarkupDTO,
)
from app.app_layer.interfaces.telegram.sender.interface import ITelegramMessageSender
from app.app_layer.interfaces.time.clock.interface import IClock
from app.app_layer.interfaces.use_cases.get_schedule_for_date.dto import (
    GetScheduleForDateUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.get_schedule_for_date.interface import (
    IGetScheduleForDateUseCase,
)
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.dto import (
    GetUpcomingLessonUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.interface import (
    IGetUpcomingLessonUseCase,
)
from app.app_layer.interfaces.use_cases.refresh_schedule.dto import (
    RefreshScheduleUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.refresh_schedule.interface import (
    IRefreshScheduleUseCase,
)
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.di.container import Container
from app.domain.messages.error import ErrorMessage
from app.domain.messages.info import InfoMessage
from app.domain.messages.notification import NotificationMessage
from app.domain.messages.schedule import ScheduleMessage
from app.domain.value_objects.timezone import Timezone
from app.logging.config import get_logger

logger = get_logger(__name__)

router = Router(name="schedule")


@router.message(Command("schedule"))
@inject
async def handle_schedule(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    get_schedule_use_case: IGetScheduleForDateUseCase = Provide[
        Container.usecases.get_schedule_for_date_use_case
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
                details=["Сначала введи /auth и открой ссылку для входа через СНИУ."],
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

    target_date = now_local.date()
    lessons = (
        await get_schedule_use_case.execute(
            GetScheduleForDateUseCaseInputDTO(account=account, target_date=target_date)
        )
    ).lessons

    await notifier.send(
        message.chat.id,
        ScheduleMessage(title="Расписание на сегодня", date=target_date, lessons=lessons),
    )


@router.message(Command("tomorrow"))
@inject
async def handle_tomorrow(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    get_schedule_use_case: IGetScheduleForDateUseCase = Provide[
        Container.usecases.get_schedule_for_date_use_case
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
                details=["Сначала введи /auth и открой ссылку для входа через СНИУ."],
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

    target_date = now_local.date() + timedelta(days=1)
    lessons = (
        await get_schedule_use_case.execute(
            GetScheduleForDateUseCaseInputDTO(account=account, target_date=target_date)
        )
    ).lessons

    await notifier.send(
        message.chat.id,
        ScheduleMessage(title="Расписание на завтра", date=target_date, lessons=lessons),
    )


@router.message(Command("next"))
@inject
async def handle_next(
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
    renderer: ITelegramMessageRenderer = Provide[Container.telegram.renderer],
    sender: ITelegramMessageSender = Provide[Container.telegram.sender],
) -> None:
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
            InfoMessage(title="Ближайшие занятия", lines=["Занятий не найдено."]),
        )
        return

    notification_message = NotificationMessage(
        title="Следующая пара",
        lesson=next_lesson.lesson,
        lesson_start=next_lesson.start_at,
    )
    rendered = renderer.render(notification_message)
    reply_markup: TelegramReplyMarkupDTO | None = None
    if next_lesson.lesson.conference_url:
        reply_markup = _conference_reply_markup(next_lesson.lesson.conference_url)
    await sender.send(message.chat.id, rendered, reply_markup=reply_markup)


def _conference_reply_markup(url: str) -> TelegramReplyMarkupDTO:
    return TelegramReplyMarkupDTO(
        inline_keyboard=((TelegramInlineKeyboardButtonDTO(text="Открыть конференцию", url=url),),)
    )


@router.message(Command("sync"))
@inject
async def handle_sync(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.usecases.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.usecases.sync_user_profile_use_case
    ],
    refresh_schedule_use_case: IRefreshScheduleUseCase = Provide[
        Container.usecases.refresh_schedule_use_case
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
                details=["Сначала введи /auth и открой ссылку для входа через СНИУ."],
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

    fetched_at = (
        await refresh_schedule_use_case.execute(
            RefreshScheduleUseCaseInputDTO(account=account, target_date=now_local.date())
        )
    ).fetched_at
    synced_at = user_now(fetched_at, timezone)

    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Расписание обновлено",
            lines=[f"Время: {synced_at.strftime('%Y-%m-%d %H:%M')}"],
        ),
    )
