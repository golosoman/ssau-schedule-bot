from pydantic import BaseModel, Field

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResult
from app.app_layer.interfaces.telegram.chat_checker.enums import TelegramChatCheckStatus
from app.app_layer.interfaces.use_cases.check_telegram_chats.dto.output import (
    CheckTelegramChatsUseCaseOutputDTO,
)


class V1CheckTelegramChatsInputSchema(BaseModel):
    chat_ids: list[int] | None = Field(default=None, min_length=1)


class V1TelegramChatCheckResultSchema(BaseModel):
    chat_id: int
    status: TelegramChatCheckStatus
    detail: str | None

    @classmethod
    def from_dto(cls, dto: TelegramChatCheckResult) -> "V1TelegramChatCheckResultSchema":
        return cls(chat_id=dto.chat_id, status=dto.status, detail=dto.detail)


class V1CheckTelegramChatsOutputSchema(BaseModel):
    checked: list[V1TelegramChatCheckResultSchema]
    total: int
    reachable: int
    not_found: int
    forbidden: int
    failed: int
    skipped: int

    @classmethod
    def from_use_case_dto(
        cls,
        dto: CheckTelegramChatsUseCaseOutputDTO,
    ) -> "V1CheckTelegramChatsOutputSchema":
        return cls(
            checked=[V1TelegramChatCheckResultSchema.from_dto(item) for item in dto.checked],
            total=dto.total,
            reachable=dto.reachable,
            not_found=dto.not_found,
            forbidden=dto.forbidden,
            failed=dto.failed,
            skipped=dto.skipped,
        )
