from abc import ABC, abstractmethod

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResultDTO


class ITelegramChatChecker(ABC):
    @abstractmethod
    async def check(self, chat_id: int) -> TelegramChatCheckResultDTO:
        raise NotImplementedError
