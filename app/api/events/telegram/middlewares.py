from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.logging.context import reset_request_id, set_request_id


class RequestIdMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        request_id = _build_request_id(event)
        token = set_request_id(request_id)
        try:
            return await handler(event, data)
        finally:
            reset_request_id(token)


def _build_request_id(event: TelegramObject) -> str:
    chat = getattr(event, "chat", None)
    message_id = getattr(event, "message_id", None)
    if chat is not None and message_id is not None:
        return f"tg-{chat.id}-{message_id}"
    return f"tg-{uuid4().hex}"
