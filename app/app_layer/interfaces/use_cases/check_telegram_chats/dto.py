from pydantic import BaseModel, ConfigDict, Field

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResultDTO


class CheckTelegramChatsUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_ids: list[int] | None = Field(default=None, min_length=1)


class CheckTelegramChatsUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    checked: list[TelegramChatCheckResultDTO]
    total: int
    reachable: int
    not_found: int
    forbidden: int
    failed: int
    skipped: int
