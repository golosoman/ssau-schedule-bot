from pydantic import BaseModel, ConfigDict

from app.domain.entities.auth import AuthSession


class LoginUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    session: AuthSession
