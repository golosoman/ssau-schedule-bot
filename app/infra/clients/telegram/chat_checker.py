from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResultDTO
from app.app_layer.interfaces.telegram.chat_checker.enums import TelegramChatCheckStatusEnum
from app.app_layer.interfaces.telegram.chat_checker.interface import ITelegramChatChecker
from app.infra.clients.telegram.interface import ITelegramBot
from app.infra.retry import RetryPolicy, retry_async
from app.logging.config import get_logger

logger = get_logger(__name__)


class TelegramChatChecker(ITelegramChatChecker):
    def __init__(self, bot: ITelegramBot, retry_policy: RetryPolicy) -> None:
        self._bot = bot
        self._retry_policy = retry_policy

    async def check(self, chat_id: int) -> TelegramChatCheckResultDTO:
        async def _operation() -> None:
            await self._bot.get_chat(chat_id)

        def _on_retry(exc: Exception, delay: float, attempt: int) -> None:
            logger.warning(
                "Telegram getChat retry %s in %.2fs (%s)",
                attempt,
                delay,
                exc,
            )

        try:
            await retry_async(
                _operation,
                policy=self._retry_policy,
                is_retryable=lambda exc: isinstance(
                    exc,
                    (TelegramNetworkError, TelegramRetryAfter),
                ),
                on_retry=_on_retry,
            )
        except TelegramForbiddenError as exc:
            return TelegramChatCheckResultDTO(
                chat_id=chat_id,
                status=TelegramChatCheckStatusEnum.FORBIDDEN,
                detail=_exception_detail(exc),
            )
        except TelegramBadRequest as exc:
            detail = _exception_detail(exc)
            if "chat not found" in detail.lower():
                return TelegramChatCheckResultDTO(
                    chat_id=chat_id,
                    status=TelegramChatCheckStatusEnum.NOT_FOUND,
                    detail=detail,
                )
            return TelegramChatCheckResultDTO(
                chat_id=chat_id,
                status=TelegramChatCheckStatusEnum.FAILED,
                detail=detail,
            )
        except Exception as exc:
            logger.exception("Telegram getChat failed for chat %s.", chat_id)
            return TelegramChatCheckResultDTO(
                chat_id=chat_id,
                status=TelegramChatCheckStatusEnum.FAILED,
                detail=_exception_detail(exc),
            )
        return TelegramChatCheckResultDTO(
            chat_id=chat_id,
            status=TelegramChatCheckStatusEnum.REACHABLE,
        )


def _exception_detail(exc: Exception) -> str:
    message = getattr(exc, "message", None)
    if isinstance(message, str) and message:
        return message
    return str(exc)
