from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.use_cases.authenticate_user.enums import (
    AuthenticateUserStatusEnum,
)


class V1AuthSsauInputSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    token: str
    login: str
    password: str


class V1AuthSsauOutputSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: AuthenticateUserStatusEnum
    group_name: str | None
