from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.telegram.chat_checker.enums import TelegramChatCheckStatusEnum


class TelegramChatCheckResultDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_id: int
    status: TelegramChatCheckStatusEnum
    detail: str | None = None
