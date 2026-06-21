from pydantic import BaseModel, ConfigDict, Field


class CheckTelegramChatsUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_ids: list[int] | None = Field(default=None, min_length=1)

