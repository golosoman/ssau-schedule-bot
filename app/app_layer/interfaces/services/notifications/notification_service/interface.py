from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.notifications.notification_service.dto.input import (
    NotificationServiceInputDTO,
)
from app.app_layer.interfaces.services.notifications.notification_service.dto.output import (
    NotificationServiceOutputDTO,
)


class INotificationService(ABC):
    @abstractmethod
    async def process_user(
        self,
        input_dto: NotificationServiceInputDTO,
    ) -> NotificationServiceOutputDTO:
        raise NotImplementedError
