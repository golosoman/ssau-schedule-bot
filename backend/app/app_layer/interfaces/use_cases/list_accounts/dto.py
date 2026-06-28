from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class ListAccountsUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    accounts: list[AccountViewDTO]
