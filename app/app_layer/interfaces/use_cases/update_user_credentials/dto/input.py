from pydantic import BaseModel, ConfigDict


class UpdateUserCredentialsUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    login: str
    password: str
