from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountView


class SyncUserProfileUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountView
