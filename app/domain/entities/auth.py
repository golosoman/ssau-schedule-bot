from pydantic import BaseModel, ConfigDict


class AuthSession(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    auth_cookie: str
