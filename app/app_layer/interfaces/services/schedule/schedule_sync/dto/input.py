from datetime import date

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountView


class ScheduleSyncForUserInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountView
    target_date: date


class ScheduleSyncIfStaleInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountView
    target_date: date
