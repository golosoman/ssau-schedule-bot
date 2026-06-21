from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.telegram.chat_checker.enums import TelegramChatCheckStatus


class TelegramChatCheckResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_id: int
    status: TelegramChatCheckStatus
    detail: str | None = None
