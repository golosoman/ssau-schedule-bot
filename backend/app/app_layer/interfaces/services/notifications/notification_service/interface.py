from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.notifications.notification_service.dto import (
    NotificationServiceInputDTO,
    NotificationServiceOutputDTO,
)


class INotificationService(ABC):
    @abstractmethod
    async def process_user(
        self,
        input_dto: NotificationServiceInputDTO,
    ) -> NotificationServiceOutputDTO:
        raise NotImplementedError
