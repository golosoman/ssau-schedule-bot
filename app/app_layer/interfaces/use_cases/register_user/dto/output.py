from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountView


class RegisterUserUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountView
