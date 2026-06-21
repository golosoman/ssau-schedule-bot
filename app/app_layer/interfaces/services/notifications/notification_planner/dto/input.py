from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.notifications.lesson_notification.dto import LessonNotification
from app.app_layer.interfaces.repos.account.dto import AccountView


class NotificationPlannerCollectDueInputDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    account: AccountView
    now: datetime


class NotificationPlannerMarkSentInputDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    notification: LessonNotification
    sent_at: datetime | None = None
