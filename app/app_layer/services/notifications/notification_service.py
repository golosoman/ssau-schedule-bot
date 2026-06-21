from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.services.notifications.notification_planner.dto.input import (
    NotificationPlannerCollectDueInputDTO,
    NotificationPlannerMarkSentInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_planner.interface import (
    INotificationPlannerService,
)
from app.app_layer.interfaces.services.notifications.notification_service.dto.input import (
    NotificationServiceInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_service.dto.output import (
    NotificationServiceOutputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_service.interface import (
    INotificationService,
)
from app.app_layer.interfaces.time.clock.interface import IClock
from app.domain.messages.notification import NotificationMessage
from app.domain.value_objects.notification_type import NotificationType
from app.logging.config import get_logger

logger = get_logger(__name__)


class NotificationService(INotificationService):
    def __init__(
        self,
        planner: INotificationPlannerService,
        notifier: INotifier,
        clock: IClock,
    ) -> None:
        self._planner = planner
        self._notifier = notifier
        self._clock = clock

    async def process_user(
        self,
        input_dto: NotificationServiceInputDTO,
    ) -> NotificationServiceOutputDTO:
        account = input_dto.account
        now = self._clock.now()
        due = await self._planner.collect_due(
            NotificationPlannerCollectDueInputDTO(
                account=account,
                now=now,
            )
        )
        if not due.notifications:
            return NotificationServiceOutputDTO(sent_count=0)

        sent = 0
        for notification in due.notifications:
            await self._notifier.send(
                notification.account.telegram.chat_id,
                NotificationMessage(
                    lesson=notification.lesson,
                    lesson_start=notification.lesson_start,
                    title=_notification_title(notification.notification_type),
                ),
            )
            await self._planner.mark_sent(
                NotificationPlannerMarkSentInputDTO(
                    notification=notification,
                    sent_at=now,
                )
            )
            sent += 1

        logger.info(
            "Notifications sent: account=%s count=%s",
            account.account_id,
            sent,
        )
        return NotificationServiceOutputDTO(sent_count=sent)


def _notification_title(notification_type: NotificationType) -> str:
    if notification_type == NotificationType.AT_START:
        return "Пара началась"
    return "Напоминание"
