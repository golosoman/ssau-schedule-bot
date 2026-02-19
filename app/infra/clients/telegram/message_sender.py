from __future__ import annotations

import logging
from collections.abc import Iterable

from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, MessageEntity

from app.app_layer.interfaces.telegram.renderer.dto import (
    RenderedTelegramMessage,
    TelegramEntity,
)
from app.domain.constants import TELEGRAM_MESSAGE_MAX_LENGTH
from app.infra.clients.telegram.message_splitter import split_message
from app.infra.retry import RetryPolicy, retry_async

logger = logging.getLogger(__name__)


class TelegramMessageSender:
    def __init__(self, bot: Bot, retry_policy: RetryPolicy) -> None:
        self._bot = bot
        self._retry_policy = retry_policy

    async def send(
        self,
        chat_id: int,
        message: RenderedTelegramMessage,
        *,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        chunks = split_message(message, limit=TELEGRAM_MESSAGE_MAX_LENGTH)
        logger.info(
            "Telegram message prepared: chat_id=%s length=%s entities=%s chunks=%s",
            chat_id,
            message.length,
            len(message.entities),
            len(chunks),
        )
        if len(chunks) > 1:
            logger.info("Telegram message split into %s chunks.", len(chunks))

        for index, chunk in enumerate(chunks):
            await self._send_chunk(
                chat_id,
                chunk,
                reply_markup=reply_markup if index == 0 else None,
            )

    async def _send_chunk(
        self,
        chat_id: int,
        chunk: RenderedTelegramMessage,
        *,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        entities = _to_aiogram_entities(chunk.entities)

        async def _operation() -> None:
            await self._bot.send_message(
                chat_id,
                chunk.text,
                entities=entities,
                reply_markup=reply_markup,
            )

        def _on_retry(exc: Exception, delay: float, attempt: int) -> None:
            logger.warning(
                "Telegram send retry %s in %.2fs (%s)",
                attempt,
                delay,
                exc,
            )

        await retry_async(
            _operation,
            policy=self._retry_policy,
            is_retryable=lambda exc: isinstance(
                exc,
                (TelegramNetworkError, TelegramRetryAfter),
            ),
            on_retry=_on_retry,
        )


def _to_aiogram_entities(entities: Iterable[TelegramEntity]) -> list[MessageEntity]:
    return [
        MessageEntity(
            type=entity.type,
            offset=entity.offset,
            length=entity.length,
            url=entity.url,
            language=entity.language,
        )
        for entity in entities
    ]
