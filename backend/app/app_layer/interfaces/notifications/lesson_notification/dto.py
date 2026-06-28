from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.domain.entities.lesson import Lesson
from app.domain.value_objects.notification_type import NotificationTypeEnum


class LessonNotificationDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
    lesson: Lesson
    lesson_start: datetime
    notification_type: NotificationTypeEnum
