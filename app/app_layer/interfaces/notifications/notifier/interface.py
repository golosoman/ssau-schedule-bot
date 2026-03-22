from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.messages.base import TelegramMessage


class INotifier(ABC):
    @abstractmethod
    async def send(self, chat_id: int, message: TelegramMessage) -> None:
        raise NotImplementedError
