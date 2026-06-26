from abc import ABC, abstractmethod

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessageDTO
from app.domain.messages.base import TelegramMessage


class ITelegramMessageRenderer(ABC):
    @abstractmethod
    def render(self, message: TelegramMessage) -> RenderedTelegramMessageDTO:
        raise NotImplementedError
