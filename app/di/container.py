from __future__ import annotations

from aiogram import Bot
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.app_layer.interfaces.http.ssau.interface import (
    IScheduleProvider,
    ISSAUProfileProvider,
)
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher
from app.app_layer.interfaces.services.notifications.notification_planner.interface import (
    INotificationPlannerService,
)
from app.app_layer.interfaces.services.notifications.notification_service.interface import (
    INotificationService,
)
from app.app_layer.interfaces.services.schedule.daily_schedule.interface import (
    IDailyScheduleService,
)
from app.app_layer.interfaces.services.schedule.lesson_date_resolver.interface import (
    ILessonDateResolverService,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.upcoming_lesson.interface import (
    IUpcomingLessonService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.telegram.renderer.interface import ITelegramMessageRenderer
from app.app_layer.interfaces.telegram.sender.interface import ITelegramMessageSender
from app.app_layer.interfaces.time.clock.interface import IClock
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.interface import (
    IUpdateUserCredentialsUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_settings.interface import (
    IUpdateUserSettingsUseCase,
)
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.services.notifications.notification_planner import NotificationPlanner
from app.app_layer.services.notifications.notification_service import NotificationService
from app.app_layer.services.schedule.daily_schedule import DailyScheduleService
from app.app_layer.services.schedule.lesson_date_resolver import LessonDateResolver
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.services.schedule.upcoming_lesson import UpcomingLessonService
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.app_layer.use_cases.update_user_credentials import UpdateUserCredentialsUseCase
from app.app_layer.use_cases.update_user_settings import UpdateUserSettingsUseCase
from app.domain.value_objects.timezone import Timezone
from app.infra.clients.ssau.ssau_client import AuthSessionCache, SSAUClient
from app.infra.clients.ssau.ssau_profile_provider import (
    SSAUProfileHttpProvider,
)
from app.infra.clients.ssau.ssau_schedule_provider import SSAUScheduleProvider
from app.infra.clients.telegram.message_renderer import AiogramTelegramMessageRenderer
from app.infra.clients.telegram.message_sender import TelegramMessageSender
from app.infra.clients.telegram.notifier import TelegramNotifier
from app.infra.db import create_engine, create_session_factory
from app.infra.retry import RetryPolicy
from app.infra.security.password_cipher import (
    FernetPasswordCipher,
    PlaintextPasswordCipher,
)
from app.infra.time.system_clock import SystemClock
from app.infra.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.settings.config import RetrySettings, Settings, get_settings


def _database_url(settings: Settings) -> str:
    return settings.database.url


def _ssau_base_url(settings: Settings) -> str:
    return settings.ssau.base_url


def _ssau_retry_policy(settings: Settings) -> RetryPolicy:
    return _build_retry_policy(settings.ssau.retry)


def _telegram_retry_policy(settings: Settings) -> RetryPolicy:
    return _build_retry_policy(settings.telegram.retry)


def _build_retry_policy(settings: RetrySettings) -> RetryPolicy:
    return RetryPolicy(
        max_attempts=settings.max_attempts,
        base_delay=settings.base_seconds,
        max_delay=settings.max_seconds,
        jitter=settings.jitter_seconds,
    )


def _password_cipher(settings: Settings) -> IPasswordCipher:
    if settings.security.fernet_key:
        return FernetPasswordCipher(settings.security.fernet_key)
    return PlaintextPasswordCipher()


def _default_timezone(settings: Settings) -> Timezone:
    return Timezone(value=settings.notifications.default_timezone)


class Container(containers.DeclarativeContainer):
    settings: providers.Provider[Settings] = providers.Singleton(get_settings)
    clock: providers.Provider[IClock] = providers.Singleton(SystemClock)
    telegram_bot: providers.Provider[Bot] = providers.Dependency(instance_of=Bot)
    default_timezone: providers.Provider[Timezone] = providers.Singleton(
        _default_timezone,
        settings,
    )

    database_url: providers.Provider[str] = providers.Callable(_database_url, settings)
    engine: providers.Provider[AsyncEngine] = providers.Singleton(
        create_engine,
        database_url=database_url,
    )
    session_factory: providers.Provider[async_sessionmaker[AsyncSession]] = providers.Singleton(
        create_session_factory,
        engine=engine,
    )
    password_cipher: providers.Provider[IPasswordCipher] = providers.Singleton(
        _password_cipher,
        settings,
    )
    uow: providers.Provider[IUnitOfWork] = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
        password_cipher=password_cipher,
    )

    ssau_retry_policy: providers.Provider[RetryPolicy] = providers.Singleton(
        _ssau_retry_policy,
        settings,
    )
    telegram_retry_policy: providers.Provider[RetryPolicy] = providers.Singleton(
        _telegram_retry_policy,
        settings,
    )
    telegram_renderer: providers.Provider[ITelegramMessageRenderer] = providers.Singleton(
        AiogramTelegramMessageRenderer,
    )
    telegram_sender: providers.Provider[ITelegramMessageSender] = providers.Singleton(
        TelegramMessageSender,
        bot=telegram_bot,
        retry_policy=telegram_retry_policy,
    )
    auth_cache: providers.Provider[AuthSessionCache] = providers.Singleton(
        AuthSessionCache,
        ttl_seconds=providers.Callable(
            lambda s: s.ssau.auth.cookie_ttl_seconds,
            settings,
        ),
        min_login_interval_seconds=providers.Callable(
            lambda s: s.ssau.auth.min_login_interval_seconds,
            settings,
        ),
        clock=clock,
    )
    ssau_client: providers.Provider[SSAUClient] = providers.Singleton(
        SSAUClient,
        base_url=providers.Callable(_ssau_base_url, settings),
        auth_cache=auth_cache,
        retry_policy=ssau_retry_policy,
        timeout_seconds=providers.Callable(lambda s: s.ssau.retry.timeout_seconds, settings),
    )

    schedule_provider: providers.Provider[IScheduleProvider] = providers.Factory(
        SSAUScheduleProvider,
        client=ssau_client,
    )

    profile_provider: providers.Provider[ISSAUProfileProvider] = providers.Factory(
        SSAUProfileHttpProvider,
        client=ssau_client,
    )

    notifier: providers.Provider[INotifier] = providers.Factory(
        TelegramNotifier,
        renderer=telegram_renderer,
        sender=telegram_sender,
    )

    register_user_use_case: providers.Provider[IRegisterUserUseCase] = providers.Factory(
        RegisterUserUseCase,
        uow_factory=uow.provider,
    )
    update_user_credentials_use_case: providers.Provider[
        IUpdateUserCredentialsUseCase
    ] = (
        providers.Factory(
            UpdateUserCredentialsUseCase,
            uow_factory=uow.provider,
        )
    )
    update_user_settings_use_case: providers.Provider[IUpdateUserSettingsUseCase] = (
        providers.Factory(
            UpdateUserSettingsUseCase,
            uow_factory=uow.provider,
        )
    )
    sync_user_profile_use_case: providers.Provider[ISyncUserProfileUseCase] = (
        providers.Factory(
            SyncUserProfileUseCase,
            uow_factory=uow.provider,
            profile_provider=profile_provider,
        )
    )

    week_calculator_service: providers.Provider[IWeekCalculatorService] = (
        providers.Singleton(AcademicWeekCalculator)
    )
    daily_schedule_service: providers.Provider[IDailyScheduleService] = (
        providers.Singleton(DailyScheduleService)
    )
    upcoming_lesson_service: providers.Provider[IUpcomingLessonService] = (
        providers.Singleton(UpcomingLessonService)
    )
    lesson_date_resolver_service: providers.Provider[ILessonDateResolverService] = (
        providers.Singleton(LessonDateResolver)
    )

    schedule_sync_service: providers.Provider[IScheduleSyncService] = providers.Factory(
        ScheduleSyncService,
        provider=schedule_provider,
        clock=clock,
        week_calculator=week_calculator_service,
    )
    notification_planner: providers.Provider[INotificationPlannerService] = (
        providers.Singleton(
            NotificationPlanner,
            lead_minutes=providers.Callable(
                lambda s: s.notifications.lead_minutes,
                settings,
            ),
            timezone=default_timezone,
            week_calculator=week_calculator_service,
        )
    )
    notification_service: providers.Provider[INotificationService] = providers.Factory(
        NotificationService,
        planner=notification_planner,
        notifier=notifier,
        clock=clock,
    )
