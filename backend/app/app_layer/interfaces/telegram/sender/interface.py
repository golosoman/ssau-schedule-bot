from abc import ABC, abstractmethod

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessageDTO
from app.app_layer.interfaces.telegram.sender.dto import TelegramReplyMarkupDTO


class ITelegramMessageSender(ABC):
    @abstractmethod
    async def send(
        self,
        chat_id: int,
        message: RenderedTelegramMessageDTO,
        *,
        reply_markup: TelegramReplyMarkupDTO | None = None,
    ) -> None:
        raise NotImplementedError
