from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class RefreshScheduleUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
    target_date: date


class RefreshScheduleUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    fetched_at: datetime
