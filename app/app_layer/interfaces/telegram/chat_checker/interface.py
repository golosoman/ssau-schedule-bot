from abc import ABC, abstractmethod

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResult


class ITelegramChatChecker(ABC):
    @abstractmethod
    async def check(self, chat_id: int) -> TelegramChatCheckResult:
        raise NotImplementedError

