import logging
from datetime import datetime, timedelta
from typing import Callable
from dependency_injector.wiring import Provide, inject

from app.api.jobs.utils import send_alert
from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.app_layer.interfaces.time.clock.interface import Clock
from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.schedule.schedule_sync import ScheduleSyncService
from app.app_layer.services.schedule.week_calculator import AcademicWeekCalculator
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.di import Container
from app.domain.value_objects.timezone import Timezone
from app.infra.observability.metrics import observe_schedule_sync, observe_worker_error
from app.logging.config import reset_request_id, set_request_id
from app.settings.config import Settings

logger = logging.getLogger(__name__)


def _user_now(now_utc: datetime, timezone: Timezone) -> datetime:
    zone = timezone.tzinfo()
    return now_utc.astimezone(zone)


@inject
async def run(
    uow_factory: Callable[[], UnitOfWork] = Provide[Container.uow.provider],
    sync_service: ScheduleSyncService = Provide[Container.schedule_sync_service],
    profile_use_case: SyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    clock: Clock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
    notifier: Notifier = Provide[Container.notifier],
) -> None:
    alert_notifier = notifier if settings.alerts.enabled else None
    admin_chat_id = settings.alerts.admin_chat_id if settings.alerts.enabled else None

    try:
        async with uow_factory() as uow:
            users = await uow.users.list_enabled()

        now_utc = clock.now()
        max_age = timedelta(hours=settings.workers.schedule_fetch_interval_hours)
        for user in users:
            token = set_request_id(f"worker-sync-{user.telegram.chat_id}")
            try:
                if user.ssau.credentials is None:
                    continue
                if user.ssau.profile is None:
                    user = await profile_use_case.execute(user)
                if user.ssau.profile is None:
                    continue

                now_local = _user_now(now_utc, timezone)
                async with uow_factory() as uow:
                    await sync_service.sync_if_stale(
                        uow,
                        user,
                        now_local.date(),
                        max_age,
                    )
                    tomorrow = now_local.date() + timedelta(days=1)
                    calculator = AcademicWeekCalculator(
                        user.ssau.profile.academic_year_start
                    )
                    if calculator.get_week_number(tomorrow) != calculator.get_week_number(
                        now_local.date()
                    ):
                        await sync_service.sync_if_stale(uow, user, tomorrow, max_age)
                observe_schedule_sync("success")
            except ValueError:
                logger.warning("Invalid timezone in settings.")
                observe_schedule_sync("error")
            except Exception:
                logger.exception(
                    "Schedule sync failed for user %s.",
                    user.telegram.chat_id,
                )
                observe_schedule_sync("error")
            finally:
                reset_request_id(token)
    except Exception:
        logger.exception("Schedule sync job failed.")
        observe_worker_error("schedule_sync")
        await send_alert(alert_notifier, admin_chat_id, "Ошибка воркера синка")
