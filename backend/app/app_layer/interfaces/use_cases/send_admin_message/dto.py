from pydantic import BaseModel, ConfigDict


class SendAdminMessageUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_ids: list[int]
    text: str


class SendAdminMessageUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    sent: list[int]
    failed: list[int]
