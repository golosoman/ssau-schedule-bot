from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.notifications.lesson_notification.dto import LessonNotificationDTO
from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class NotificationPlannerCollectDueInputDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    account: AccountViewDTO
    now: datetime


class NotificationPlannerMarkSentInputDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    notification: LessonNotificationDTO
    sent_at: datetime | None = None


class NotificationPlannerCollectDueOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    notifications: list[LessonNotificationDTO]
