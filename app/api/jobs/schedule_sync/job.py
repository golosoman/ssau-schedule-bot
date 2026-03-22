import logging
from collections.abc import Callable
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject

from app.api.jobs.utils import send_alert
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.services.schedule.schedule_sync.dto.input import (
    ScheduleSyncIfStaleInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.time.clock.interface import IClock
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.sync_user_profile.dto.input import (
    SyncUserProfileUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
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
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.uow.provider],
    sync_service: IScheduleSyncService = Provide[Container.schedule_sync_service],
    profile_use_case: ISyncUserProfileUseCase = Provide[
        Container.sync_user_profile_use_case
    ],
    week_calculator: IWeekCalculatorService = Provide[Container.week_calculator_service],
    clock: IClock = Provide[Container.clock],
    timezone: Timezone = Provide[Container.default_timezone],
    settings: Settings = Provide[Container.settings],
    notifier: INotifier = Provide[Container.notifier],
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
                    user = (
                        await profile_use_case.execute(
                            SyncUserProfileUseCaseInputDTO(user=user)
                        )
                    ).user
                if user.ssau.profile is None:
                    continue

                now_local = _user_now(now_utc, timezone)
                async with uow_factory() as uow:
                    await sync_service.sync_if_stale(
                        ScheduleSyncIfStaleInputDTO(
                            uow=uow,
                            user=user,
                            target_date=now_local.date(),
                            max_age=max_age,
                        )
                    )
                    tomorrow = now_local.date() + timedelta(days=1)
                    tomorrow_week = week_calculator.get_week_number(
                        WeekCalculatorServiceInputDTO(
                            start_date=user.ssau.profile.profile_details.academic_year_start,
                            target_date=tomorrow,
                        )
                    ).week_number
                    current_week = week_calculator.get_week_number(
                        WeekCalculatorServiceInputDTO(
                            start_date=user.ssau.profile.profile_details.academic_year_start,
                            target_date=now_local.date(),
                        )
                    ).week_number
                    if tomorrow_week != current_week:
                        await sync_service.sync_if_stale(
                            ScheduleSyncIfStaleInputDTO(
                                uow=uow,
                                user=user,
                                target_date=tomorrow,
                                max_age=max_age,
                            )
                        )
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
