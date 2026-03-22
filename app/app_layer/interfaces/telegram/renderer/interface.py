from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessage
from app.domain.messages.base import TelegramMessage


class ITelegramMessageRenderer(ABC):
    @abstractmethod
    def render(self, message: TelegramMessage) -> RenderedTelegramMessage:
        raise NotImplementedError
