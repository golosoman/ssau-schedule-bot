from pydantic import BaseModel, ConfigDict


class RegisterUserUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    display_name: str
