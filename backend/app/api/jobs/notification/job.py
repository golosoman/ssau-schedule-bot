from collections.abc import Callable

from dependency_injector.wiring import Provide, inject

from app.api.jobs.utils import send_alert
from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.services.notifications.notification_service.dto import (
    NotificationServiceInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_service.interface import (
    INotificationService,
)
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.di.container import Container
from app.infra.observability.metrics.interface import IMetricsService
from app.logging.config import get_logger
from app.logging.context import reset_request_id, set_request_id
from app.settings.config import settings

logger = get_logger(__name__)


@inject
async def run(
    uow_factory: Callable[[], IUnitOfWork] = Provide[Container.db.uow_factory],
    account_repo: IAccountRepository = Provide[Container.repositories.account_repo],
    notifier: INotifier = Provide[Container.telegram.notifier],
    service: INotificationService = Provide[Container.services.notification_service],
    metrics: IMetricsService = Provide[Container.metrics.metrics_service],
) -> None:
    alert_notifier = notifier if settings.alerts.enabled else None
    admin_chat_id = settings.alerts.admin_chat_id if settings.alerts.enabled else None

    try:
        async with uow_factory():
            accounts = await account_repo.list_notifiable()

        for account in accounts:
            token = set_request_id(f"worker-notify-{account.chat_id}")
            try:
                async with uow_factory():
                    await service.process_user(NotificationServiceInputDTO(account=account))
            except Exception:
                logger.exception(
                    "Notification processing failed for account %s.",
                    account.account_id,
                )
            finally:
                reset_request_id(token)
    except Exception:
        logger.exception("Notification job failed.")
        metrics.observe_worker_error("notification")
        await send_alert(alert_notifier, admin_chat_id, "Ошибка воркера уведомлений")
