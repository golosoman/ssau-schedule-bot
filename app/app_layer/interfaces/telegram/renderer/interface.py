from __future__ import annotations

from typing import Protocol

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessage
from app.domain.messages.base import TelegramMessage


class TelegramMessageRenderer(Protocol):
    def render(self, message: TelegramMessage) -> RenderedTelegramMessage: ...
