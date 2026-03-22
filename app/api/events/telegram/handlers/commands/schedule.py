import logging
from collections.abc import Callable
from datetime import datetime, time, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import (
    credentials_missing,
    ensure_profile,
    load_user,
    sync_cache,
    user_now,
)
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.services.schedule.daily_schedule.dto.input import (
    DailyScheduleServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.daily_schedule.interface import (
    IDailyScheduleService,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.upcoming_lesson.dto.input import (
    UpcomingLessonServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.upcoming_lesson.interface import (
    IUpcomingLessonService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.telegram.renderer.interface import ITelegramMessageRenderer
from app.app_layer.interfaces.telegram.sender.interface import ITelegramMessageSender
from app.app_layer.interfaces.time.clock.interface import IClock
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.di import Container
from app.domain.constants import DAYS_IN_WEEK
from app.domain.messages.error import ErrorMessage
from app.domain.messages.info import InfoMessage
from app.domain.messages.notification import NotificationMessage
from app.domain.messages.schedule import ScheduleMessage
from app.domain.value_objects.timezone import Timezone
from app.infra.clients.telegram.keyboard_builder import TelegramKeyboardBuilder
from app.settings.config import Settings

logger = logging.getLogger(__name__)

router = Router(name="schedule")


@router.message(Command("schedule"))
@inject
async def handle_schedule(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    sync_service: IScheduleSyncService = Provide[Container.schedule_sync_service],
    week_calculator: IWeekCalculatorService = Provide[Container.week_calculator_service],
    daily_schedule_service: IDailyScheduleService = Provide[
        Container.daily_schedule_service
    ],
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.uow.provider],
    clock: IClock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
    notifier: INotifier = Provide[Container.notifier],
) -> None:
    user = await load_user(message, register_use_case)

    if credentials_missing(user):
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Нет доступа",
                details=["Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ"],
            ),
        )
        return

    try:
        user = await ensure_profile(user, sync_profile_use_case)
        now_local = user_now(clock.now(), timezone)
    except ValueError:
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Некорректная таймзона",
                details=["Сообщи администратору."],
            ),
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

    cache = await sync_cache(
        uow_factory,
        sync_service,
        user,
        now_local,
        max_age=timedelta(hours=settings.workers.schedule_fetch_interval_hours),
    )
    profile = user.ssau.profile
    if profile is None:
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Профиль не получен", details=["Не удалось получить профиль."]),
        )
        return
    week_number = week_calculator.get_week_number(
        WeekCalculatorServiceInputDTO(
            start_date=profile.profile_details.academic_year_start,
            target_date=now_local.date(),
        )
    ).week_number
    daily_lessons = daily_schedule_service.filter_for_date(
        DailyScheduleServiceInputDTO(
            lessons=cache.lessons,
            target_date=now_local.date(),
            week_number=week_number,
            subgroup=profile.profile_details.subgroup,
        )
    ).lessons

    await notifier.send(
        message.chat.id,
        ScheduleMessage(
            title="Расписание на сегодня",
            date=now_local.date(),
            lessons=daily_lessons,
        ),
    )


@router.message(Command("tomorrow"))
@inject
async def handle_tomorrow(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    sync_service: IScheduleSyncService = Provide[Container.schedule_sync_service],
    week_calculator: IWeekCalculatorService = Provide[Container.week_calculator_service],
    daily_schedule_service: IDailyScheduleService = Provide[
        Container.daily_schedule_service
    ],
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.uow.provider],
    clock: IClock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
    notifier: INotifier = Provide[Container.notifier],
) -> None:
    user = await load_user(message, register_use_case)

    if credentials_missing(user):
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Нет доступа",
                details=["Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ"],
            ),
        )
        return

    try:
        user = await ensure_profile(user, sync_profile_use_case)
        now_local = user_now(clock.now(), timezone)
    except ValueError:
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Некорректная таймзона",
                details=["Сообщи администратору."],
            ),
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

    target_date = now_local.date() + timedelta(days=1)
    cache = await sync_cache(
        uow_factory,
        sync_service,
        user,
        datetime.combine(target_date, time.min, tzinfo=now_local.tzinfo),
        max_age=timedelta(hours=settings.workers.schedule_fetch_interval_hours),
    )
    profile = user.ssau.profile
    if profile is None:
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Профиль не получен", details=["Не удалось получить профиль."]),
        )
        return
    week_number = week_calculator.get_week_number(
        WeekCalculatorServiceInputDTO(
            start_date=profile.profile_details.academic_year_start,
            target_date=target_date,
        )
    ).week_number
    daily_lessons = daily_schedule_service.filter_for_date(
        DailyScheduleServiceInputDTO(
            lessons=cache.lessons,
            target_date=target_date,
            week_number=week_number,
            subgroup=profile.profile_details.subgroup,
        )
    ).lessons

    await notifier.send(
        message.chat.id,
        ScheduleMessage(
            title="Расписание на завтра",
            date=target_date,
            lessons=daily_lessons,
        ),
    )


@router.message(Command("next"))
@inject
async def handle_next(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    sync_service: IScheduleSyncService = Provide[Container.schedule_sync_service],
    week_calculator: IWeekCalculatorService = Provide[Container.week_calculator_service],
    upcoming_lesson_service: IUpcomingLessonService = Provide[
        Container.upcoming_lesson_service
    ],
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.uow.provider],
    clock: IClock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
    notifier: INotifier = Provide[Container.notifier],
    renderer: ITelegramMessageRenderer = Provide[Container.telegram_renderer],
    sender: ITelegramMessageSender = Provide[Container.telegram_sender],
) -> None:
    user = await load_user(message, register_use_case)

    if credentials_missing(user):
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Нет доступа",
                details=["Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ"],
            ),
        )
        return

    try:
        user = await ensure_profile(user, sync_profile_use_case)
        now_local = user_now(clock.now(), timezone)
    except ValueError:
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Некорректная таймзона",
                details=["Сообщи администратору."],
            ),
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

    cache = await sync_cache(
        uow_factory,
        sync_service,
        user,
        now_local,
        max_age=timedelta(hours=settings.workers.schedule_fetch_interval_hours),
    )
    profile = user.ssau.profile
    if profile is None:
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Профиль не получен", details=["Не удалось получить профиль."]),
        )
        return
    week_number = week_calculator.get_week_number(
        WeekCalculatorServiceInputDTO(
            start_date=profile.profile_details.academic_year_start,
            target_date=now_local.date(),
        )
    ).week_number
    next_lesson = upcoming_lesson_service.find_next(
        UpcomingLessonServiceInputDTO(
            lessons=cache.lessons,
            now_local=now_local,
            week_number=week_number,
            subgroup=profile.profile_details.subgroup,
        )
    ).upcoming_lesson

    if next_lesson is None:
        days_until_monday = (DAYS_IN_WEEK + 1) - now_local.isoweekday()
        next_week_date = now_local.date() + timedelta(days=days_until_monday)
        next_week_local = datetime.combine(
            next_week_date,
            time.min,
            tzinfo=now_local.tzinfo,
        )
        cache = await sync_cache(
            uow_factory,
            sync_service,
            user,
            next_week_local,
            max_age=timedelta(hours=settings.workers.schedule_fetch_interval_hours),
        )
        next_week_number = week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=profile.profile_details.academic_year_start,
                target_date=next_week_date,
            )
        ).week_number
        next_lesson = upcoming_lesson_service.find_next(
            UpcomingLessonServiceInputDTO(
                lessons=cache.lessons,
                now_local=next_week_local,
                week_number=next_week_number,
                subgroup=profile.profile_details.subgroup,
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
    reply_markup = None
    if next_lesson.lesson.conference_url:
        reply_markup = TelegramKeyboardBuilder.conference(next_lesson.lesson.conference_url)
    await sender.send(message.chat.id, rendered, reply_markup=reply_markup)


@router.message(Command("sync"))
@inject
async def handle_sync(
    message: Message,
    register_use_case: IRegisterUserUseCase = Provide[Container.register_user_use_case],
    sync_profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    sync_service: IScheduleSyncService = Provide[Container.schedule_sync_service],
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.uow.provider],
    clock: IClock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
    notifier: INotifier = Provide[Container.notifier],
) -> None:
    user = await load_user(message, register_use_case)

    if credentials_missing(user):
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Нет доступа",
                details=["Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ"],
            ),
        )
        return

    try:
        user = await ensure_profile(user, sync_profile_use_case)
        now_local = user_now(clock.now(), timezone)
    except ValueError:
        await notifier.send(
            message.chat.id,
            ErrorMessage(
                title="Некорректная таймзона",
                details=["Сообщи администратору."],
            ),
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

    profile = user.ssau.profile
    if profile is None:
        await notifier.send(
            message.chat.id,
            ErrorMessage(title="Профиль не получен", details=["Не удалось получить профиль."]),
        )
        return
    cache = await sync_cache(
        uow_factory,
        sync_service,
        user,
        now_local,
        max_age=timedelta(hours=settings.workers.schedule_fetch_interval_hours),
        force=True,
    )
    synced_at = user_now(cache.fetched_at, timezone)

    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Расписание обновлено",
            lines=[f"Время: {synced_at.strftime('%Y-%m-%d %H:%M')}"],
        ),
    )
