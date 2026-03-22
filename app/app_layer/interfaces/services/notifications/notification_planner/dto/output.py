from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.notifications.lesson_notification.dto import LessonNotification


class NotificationPlannerCollectDueOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    notifications: list[LessonNotification]
