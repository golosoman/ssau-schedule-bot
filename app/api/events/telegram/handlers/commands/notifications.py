import logging
from datetime import datetime, time, timedelta
from typing import Callable

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import (
    command_args,
    credentials_missing,
    ensure_profile,
    load_user,
    sync_cache,
    user_now,
)
from app.app_layer.interfaces.time.clock.interface import Clock
from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.notifications.notification_message import format_notification
from app.app_layer.interfaces.notifications.lesson_notification.dto import (
    LessonNotification,
)
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.services.schedule.upcoming_lesson import UpcomingLessonService
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.app_layer.use_cases.update_user_settings import UpdateUserSettingsUseCase
from app.di import Container
from app.domain.value_objects.timezone import Timezone
from app.settings.config import Settings

logger = logging.getLogger(__name__)

router = Router(name="notifications")


@router.message(Command("notify"))
@inject
async def handle_notify(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
    update_settings_use_case: UpdateUserSettingsUseCase = Provide[
        Container.update_user_settings_use_case
    ],
) -> None:
    args = command_args(message)
    if not args or args[0] not in {"on", "off"}:
        await message.answer("Использование: /notify on|off")
        return

    enabled = args[0] == "on"
    await load_user(message, register_use_case)
    await update_settings_use_case.execute(message.chat.id, notify_enabled=enabled)

    await message.answer(f"Уведомления {'включены' if enabled else 'выключены'}.")


@router.message(Command("notify_test"))
@inject
async def handle_notify_test(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
    sync_profile_use_case: SyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    sync_service: ScheduleSyncService = Provide[Container.schedule_sync_service],
    uow_factory: Callable[[], UnitOfWork] = Provide[Container.uow.provider],
    clock: Clock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
) -> None:
    user = await load_user(message, register_use_case)

    if credentials_missing(user):
        await message.answer("Сначала укажи логин/пароль: /auth ЛОГИН ПАРОЛЬ")
        return

    try:
        user = await ensure_profile(user, sync_profile_use_case)
        now_local = user_now(clock.now(), timezone)
    except ValueError:
        await message.answer("Некорректная таймзона в настройках. Сообщи администратору.")
        return
    except Exception:
        logger.exception("Profile sync failed for user %s.", message.chat.id)
        await message.answer("Не удалось получить данные профиля (группа/год).")
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
        await message.answer("Не удалось получить профиль (группа/год).")
        return
    week_number = AcademicWeekCalculator(profile.academic_year_start).get_week_number(
        now_local.date()
    )
    next_lesson = UpcomingLessonService.find_next(
        cache.lessons,
        now_local,
        week_number,
        profile.subgroup,
    )

    if next_lesson is None:
        days_until_monday = 8 - now_local.isoweekday()
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
        next_week_number = AcademicWeekCalculator(
            profile.academic_year_start
        ).get_week_number(next_week_date)
        next_lesson = UpcomingLessonService.find_next(
            cache.lessons,
            next_week_local,
            next_week_number,
            profile.subgroup,
        )

    if next_lesson is None:
        await message.answer("Тестовое уведомление: ближайших занятий не найдено.")
        return

    notification = LessonNotification(
        user=user,
        lesson=next_lesson.lesson,
        lesson_start=next_lesson.start_at,
    )
    await message.answer(f"ТЕСТ\n{format_notification(notification)}")
