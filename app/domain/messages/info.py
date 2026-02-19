from __future__ import annotations

from app.domain.messages.base import TelegramMessage


class InfoMessage(TelegramMessage):
    title: str
    lines: list[str]
