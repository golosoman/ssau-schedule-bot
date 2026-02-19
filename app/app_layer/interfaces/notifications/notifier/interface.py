from __future__ import annotations

from typing import Protocol

from app.domain.messages.base import TelegramMessage


class Notifier(Protocol):
    async def send(self, chat_id: int, message: TelegramMessage) -> None: ...
