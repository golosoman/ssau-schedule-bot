from __future__ import annotations

from app.domain.messages.base import TelegramMessage


class ErrorMessage(TelegramMessage):
    title: str
    details: list[str] | None = None
