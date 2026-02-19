import logging

from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.app_layer.interfaces.time.clock.interface import Clock
from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.app_layer.services.notifications.notification_planner import NotificationPlanner
from app.domain.entities.users import User
from app.domain.messages.notification import NotificationMessage

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        planner: NotificationPlanner,
        notifier: Notifier,
        clock: Clock,
    ) -> None:
        self._planner = planner
        self._notifier = notifier
        self._clock = clock

    async def process_user(self, uow: UnitOfWork, user: User) -> int:
        now = self._clock.now()
        due = await self._planner.collect_due(uow, user, now)
        if not due:
            return 0

        sent = 0
        for notification in due:
            await self._notifier.send(
                notification.user.telegram.chat_id,
                NotificationMessage(
                    lesson=notification.lesson,
                    lesson_start=notification.lesson_start,
                ),
            )
            await self._planner.mark_sent(uow, notification, sent_at=now)
            sent += 1

        logger.info("Notifications sent: user=%s count=%s", user.telegram.chat_id, sent)
        return sent
