from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.app_layer.interfaces.schedule.upcoming_lesson.dto import UpcomingLessonDTO


class GetUpcomingLessonUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
    now_local: datetime


class GetUpcomingLessonUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    upcoming_lesson: UpcomingLessonDTO | None
