from collections.abc import Callable
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject

from app.api.jobs.utils import send_alert
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.services.schedule.schedule_sync.dto.input import (
    ScheduleSyncForUserInputDTO,
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
from app.di.container import Container
from app.domain.value_objects.timezone import Timezone
from app.infra.observability.metrics.interface import IMetricsService
from app.logging.config import get_logger
from app.logging.context import reset_request_id, set_request_id
from app.settings.config import settings

logger = get_logger(__name__)


def _user_now(now_utc: datetime, timezone: Timezone) -> datetime:
    zone = timezone.tzinfo()
    return now_utc.astimezone(zone)


@inject
async def run(
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.db.uow_factory],
    account_repo: IAccountRepository = Provide[Container.repositories.account_repo],
    sync_service: IScheduleSyncService = Provide[Container.services.schedule_sync_service],
    week_calculator: IWeekCalculatorService = Provide[Container.services.week_calculator_service],
    clock: IClock = Provide[Container.core.clock],
    timezone: Timezone = Provide[Container.core.default_timezone],
    notifier: INotifier = Provide[Container.telegram.notifier],
    metrics: IMetricsService = Provide[Container.metrics.metrics_service],
) -> None:
    alert_notifier = notifier if settings.alerts.enabled else None
    admin_chat_id = settings.alerts.admin_chat_id if settings.alerts.enabled else None

    try:
        async with uow_factory():
            accounts = await account_repo.list_notifiable()

        now_utc = clock.now()
        for account in accounts:
            profile = account.ssau_profile
            if profile is None:
                continue
            token = set_request_id(f"worker-sync-{account.chat_id}")
            try:
                now_local = _user_now(now_utc, timezone)
                await sync_service.sync_for_user(
                    ScheduleSyncForUserInputDTO(account=account, target_date=now_local.date())
                )
                tomorrow = now_local.date() + timedelta(days=1)
                tomorrow_week = week_calculator.get_week_number(
                    WeekCalculatorServiceInputDTO(
                        start_date=profile.academic_year_start,
                        target_date=tomorrow,
                    )
                ).week_number
                current_week = week_calculator.get_week_number(
                    WeekCalculatorServiceInputDTO(
                        start_date=profile.academic_year_start,
                        target_date=now_local.date(),
                    )
                ).week_number
                if tomorrow_week != current_week:
                    await sync_service.sync_for_user(
                        ScheduleSyncForUserInputDTO(account=account, target_date=tomorrow)
                    )
                metrics.observe_schedule_sync("success")
            except ValueError:
                logger.warning("Invalid timezone in settings.")
                metrics.observe_schedule_sync("error")
            except Exception:
                logger.exception("Schedule sync failed for account %s.", account.account_id)
                metrics.observe_schedule_sync("error")
            finally:
                reset_request_id(token)
    except Exception:
        logger.exception("Schedule sync job failed.")
        metrics.observe_worker_error("schedule_sync")
        await send_alert(alert_notifier, admin_chat_id, "Ошибка воркера синка")
