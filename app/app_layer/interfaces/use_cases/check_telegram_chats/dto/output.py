from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResult


class CheckTelegramChatsUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    checked: list[TelegramChatCheckResult]
    total: int
    reachable: int
    not_found: int
    forbidden: int
    failed: int
    skipped: int

