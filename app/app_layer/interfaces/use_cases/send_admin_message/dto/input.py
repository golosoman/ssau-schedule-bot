from pydantic import BaseModel, ConfigDict


class SendAdminMessageUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_ids: list[int]
    text: str
