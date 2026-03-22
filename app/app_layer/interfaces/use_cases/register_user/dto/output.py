from pydantic import BaseModel, ConfigDict

from app.domain.entities.users import User


class RegisterUserUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    user: User
