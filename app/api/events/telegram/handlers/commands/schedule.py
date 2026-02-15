import logging
from datetime import datetime, time, timedelta
from typing import Callable
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import (
    credentials_missing,
    ensure_profile,
    format_lessons,
    format_next_lesson,
    load_user,
    sync_cache,
    user_now,
)
from app.app_layer.interfaces.time.clock.interface import Clock
from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.schedule.daily_schedule import DailyScheduleService
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.services.schedule.upcoming_lesson import UpcomingLessonService
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.di import Container
from app.domain.value_objects.timezone import Timezone
from app.settings.config import Settings

logger = logging.getLogger(__name__)

router = Router(name="schedule")


@router.message(Command("schedule"))
@inject
async def handle_schedule(
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
    daily_lessons = DailyScheduleService.filter_for_date(
        cache.lessons,
        now_local.date(),
        week_number,
        profile.subgroup,
    )

    await message.answer(format_lessons(daily_lessons))


@router.message(Command("tomorrow"))
@inject
async def handle_tomorrow(
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
        await message.answer("Не удалось получить профиль (группа/год).")
        return
    week_number = AcademicWeekCalculator(profile.academic_year_start).get_week_number(
        target_date
    )
    daily_lessons = DailyScheduleService.filter_for_date(
        cache.lessons,
        target_date,
        week_number,
        profile.subgroup,
    )

    await message.answer(format_lessons(daily_lessons))


@router.message(Command("next"))
@inject
async def handle_next(
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
        await message.answer("Ближайших занятий не найдено.")
        return

    await message.answer(format_next_lesson(next_lesson.start_at, next_lesson.lesson))


@router.message(Command("sync"))
@inject
async def handle_sync(
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

    profile = user.ssau.profile
    if profile is None:
        await message.answer("Не удалось получить профиль (группа/год).")
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

    await message.answer(
        f"Расписание обновлено в {synced_at.strftime('%Y-%m-%d %H:%M')}."
    )
