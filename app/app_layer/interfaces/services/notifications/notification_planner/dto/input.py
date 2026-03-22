from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.notifications.lesson_notification.dto import LessonNotification
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.domain.entities.users import User


class NotificationPlannerCollectDueInputDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    uow: IUnitOfWork
    user: User
    now: datetime


class NotificationPlannerMarkSentInputDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    uow: IUnitOfWork
    notification: LessonNotification
    sent_at: datetime | None = None
