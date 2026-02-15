from uuid import uuid4

from aiogram import BaseMiddleware

from app.logging.config import reset_request_id, set_request_id


class RequestIdMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        request_id = _build_request_id(event)
        token = set_request_id(request_id)
        try:
            return await handler(event, data)
        finally:
            reset_request_id(token)


def _build_request_id(event) -> str:
    chat = getattr(event, "chat", None)
    message_id = getattr(event, "message_id", None)
    if chat is not None and message_id is not None:
        return f"tg-{chat.id}-{message_id}"
    return f"tg-{uuid4().hex}"
