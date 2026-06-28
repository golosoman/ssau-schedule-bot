from collections.abc import Iterable

from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity

from app.app_layer.interfaces.telegram.renderer.dto import (
    RenderedTelegramMessageDTO,
    TelegramEntityDTO,
)
from app.app_layer.interfaces.telegram.sender.dto import TelegramReplyMarkupDTO
from app.app_layer.interfaces.telegram.sender.interface import (
    ITelegramMessageSender,
)
from app.domain.constants import TELEGRAM_MESSAGE_MAX_LENGTH
from app.infra.clients.telegram.interface import ITelegramBot
from app.infra.clients.telegram.message_splitter import split_message
from app.infra.retry import RetryPolicy, retry_async
from app.logging.config import get_logger

logger = get_logger(__name__)


class TelegramMessageSender(ITelegramMessageSender):
    def __init__(self, bot: ITelegramBot, retry_policy: RetryPolicy) -> None:
        self._bot = bot
        self._retry_policy = retry_policy

    async def send(
        self,
        chat_id: int,
        message: RenderedTelegramMessageDTO,
        *,
        reply_markup: TelegramReplyMarkupDTO | None = None,
    ) -> None:
        chunks = split_message(message, limit=TELEGRAM_MESSAGE_MAX_LENGTH)
        aiogram_reply_markup = _to_aiogram_reply_markup(reply_markup)
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
                reply_markup=aiogram_reply_markup if index == 0 else None,
            )

    async def _send_chunk(
        self,
        chat_id: int,
        chunk: RenderedTelegramMessageDTO,
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


def _to_aiogram_entities(entities: Iterable[TelegramEntityDTO]) -> list[MessageEntity]:
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


def _to_aiogram_reply_markup(markup: TelegramReplyMarkupDTO | None) -> InlineKeyboardMarkup | None:
    if markup is None:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button.text,
                    url=button.url,
                    callback_data=button.callback_data,
                )
                for button in row
            ]
            for row in markup.inline_keyboard
        ]
    )
