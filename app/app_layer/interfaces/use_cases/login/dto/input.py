from pydantic import BaseModel, ConfigDict


class LoginUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    login: str
    password: str
