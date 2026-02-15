import logging
from typing import Callable
from dependency_injector.wiring import Provide, inject

from app.api.jobs.utils import send_alert
from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.notifications.notification_service import NotificationService
from app.di import Container
from app.infra.observability.metrics import observe_worker_error
from app.logging.config import reset_request_id, set_request_id
from app.settings.config import Settings

logger = logging.getLogger(__name__)


@inject
async def run(
    uow_factory: Callable[[], UnitOfWork] = Provide[Container.uow.provider],
    notifier: Notifier = Provide[Container.notifier],
    service: NotificationService = Provide[Container.notification_service],
    settings: Settings = Provide[Container.settings],
) -> None:
    alert_notifier = notifier if settings.alerts.enabled else None
    admin_chat_id = settings.alerts.admin_chat_id if settings.alerts.enabled else None

    try:
        async with uow_factory() as uow:
            users = await uow.users.list_enabled()

        for user in users:
            token = set_request_id(f"worker-notify-{user.telegram.chat_id}")
            try:
                if user.ssau.credentials is None:
                    continue
                if user.ssau.profile is None:
                    continue
                async with uow_factory() as uow:
                    await service.process_user(uow, user)
            except Exception:
                logger.exception(
                    "Notification processing failed for user %s.",
                    user.telegram.chat_id,
                )
            finally:
                reset_request_id(token)
    except Exception:
        logger.exception("Notification job failed.")
        observe_worker_error("notification")
        await send_alert(alert_notifier, admin_chat_id, "Ошибка воркера уведомлений")
