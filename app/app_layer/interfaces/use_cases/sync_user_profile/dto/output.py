from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountView


class SyncUserProfileUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountView
