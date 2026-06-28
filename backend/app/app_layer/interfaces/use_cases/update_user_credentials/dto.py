from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class UpdateUserCredentialsUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    login: str
    password: str


class UpdateUserCredentialsUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
