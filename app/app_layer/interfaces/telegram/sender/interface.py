from __future__ import annotations

from abc import ABC, abstractmethod

from aiogram.types import InlineKeyboardMarkup

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessage


class ITelegramMessageSender(ABC):
    @abstractmethod
    async def send(
        self,
        chat_id: int,
        message: RenderedTelegramMessage,
        *,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        raise NotImplementedError
