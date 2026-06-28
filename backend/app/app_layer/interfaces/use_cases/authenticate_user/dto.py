from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.app_layer.interfaces.use_cases.authenticate_user.enums import (
    AuthenticateUserStatusEnum,
)


class AuthenticateUserUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_id: int
    login: str
    password: str


class AuthenticateUserUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: AuthenticateUserStatusEnum
    account: AccountViewDTO
