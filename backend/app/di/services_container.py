from dependency_injector import containers, providers

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
from app.app_layer.services.notifications.notification_planner import NotificationPlanner
from app.app_layer.services.notifications.notification_service import NotificationService
from app.app_layer.services.schedule.daily_schedule import DailyScheduleService
from app.app_layer.services.schedule.lesson_date_resolver import LessonDateResolver
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.services.schedule.upcoming_lesson import UpcomingLessonService
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.settings.config import settings


class ServicesContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    cache = providers.DependenciesContainer()
    ssau = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    telegram = providers.DependenciesContainer()

    week_calculator_service: providers.Provider[IWeekCalculatorService] = providers.Singleton(
        AcademicWeekCalculator
    )
    daily_schedule_service: providers.Provider[IDailyScheduleService] = providers.Singleton(
        DailyScheduleService
    )
    upcoming_lesson_service: providers.Provider[IUpcomingLessonService] = providers.Singleton(
        UpcomingLessonService
    )
    lesson_date_resolver_service: providers.Provider[ILessonDateResolverService] = (
        providers.Singleton(LessonDateResolver)
    )

    schedule_sync_service: providers.Provider[IScheduleSyncService] = providers.Factory(
        ScheduleSyncService,
        provider=ssau.api_client,
        clock=core.clock,
        week_calculator=week_calculator_service,
        cache_store=cache.schedule_cache_store,
    )
    notification_planner: providers.Provider[INotificationPlannerService] = providers.Singleton(
        NotificationPlanner,
        lead_minutes=settings.notifications.lead_minutes,
        timezone=core.default_timezone,
        week_calculator=week_calculator_service,
        cache_store=cache.schedule_cache_store,
        notification_log_repo=repositories.notification_log_repo,
    )
    notification_service: providers.Provider[INotificationService] = providers.Factory(
        NotificationService,
        planner=notification_planner,
        notifier=telegram.notifier,
        clock=core.clock,
    )
