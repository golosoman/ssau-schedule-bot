from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.notifications.notification_planner.dto.input import (
    NotificationPlannerCollectDueInputDTO,
    NotificationPlannerMarkSentInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_planner.dto.output import (
    NotificationPlannerCollectDueOutputDTO,
)


class INotificationPlannerService(ABC):
    @abstractmethod
    async def collect_due(
        self,
        input_dto: NotificationPlannerCollectDueInputDTO,
    ) -> NotificationPlannerCollectDueOutputDTO:
        raise NotImplementedError

    @abstractmethod
    async def mark_sent(self, input_dto: NotificationPlannerMarkSentInputDTO) -> None:
        raise NotImplementedError
