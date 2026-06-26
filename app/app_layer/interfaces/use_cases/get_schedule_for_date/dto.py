from datetime import date

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.domain.entities.lesson import Lesson


class GetScheduleForDateUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
    target_date: date


class GetScheduleForDateUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    lessons: list[Lesson]
