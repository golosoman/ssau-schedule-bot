from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class RegisterUserUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    display_name: str


class RegisterUserUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
