from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class SyncUserProfileUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO


class SyncUserProfileUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
