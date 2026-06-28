from abc import ABC, abstractmethod

from aiogram.types import ChatFullInfo, InlineKeyboardMarkup, MessageEntity


class ITelegramBot(ABC):
    """Контракт телеграм-бота для отправки сообщений (порт над aiogram.Bot)."""

    @abstractmethod
    async def get_chat(self, chat_id: int) -> ChatFullInfo:
        raise NotImplementedError

    @abstractmethod
    async def send_message(
        self,
        chat_id: int,
        text: str,
        *,
        entities: list[MessageEntity] | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        raise NotImplementedError
