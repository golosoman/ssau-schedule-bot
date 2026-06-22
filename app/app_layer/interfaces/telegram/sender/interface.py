from abc import ABC, abstractmethod

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessage
from app.app_layer.interfaces.telegram.sender.dto import TelegramReplyMarkup


class ITelegramMessageSender(ABC):
    @abstractmethod
    async def send(
        self,
        chat_id: int,
        message: RenderedTelegramMessage,
        *,
        reply_markup: TelegramReplyMarkup | None = None,
    ) -> None:
        raise NotImplementedError
