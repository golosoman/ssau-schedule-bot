import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError, TelegramRetryAfter

try:
    from aiogram.exceptions import TelegramUnauthorized
except ImportError:
    try:
        from aiogram.exceptions import TelegramUnauthorizedError as TelegramUnauthorized
    except ImportError:
        TelegramUnauthorized = TelegramAPIError

from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.infra.observability.metrics import observe_telegram_send
from app.infra.observability.telemetry import get_tracer
from app.infra.retry import RetryPolicy, retry_async

logger = logging.getLogger(__name__)


class TelegramNotifier(Notifier):
    def __init__(self, bot: Bot, retry_policy: RetryPolicy) -> None:
        self._bot = bot
        self._retry_policy = retry_policy
        self._tracer = get_tracer(__name__)

    async def send(self, chat_id: int, text: str) -> None:
        async def _operation() -> None:
            with self._tracer.start_as_current_span("telegram.send") as span:
                span.set_attribute("telegram.chat_id", chat_id)
                await self._bot.send_message(chat_id, text)

        def _on_retry(exc: Exception, delay: float, attempt: int) -> None:
            logger.warning("Telegram retry %s in %.2fs (%s)", attempt, delay, exc)

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
            observe_telegram_send("success")
        except TelegramUnauthorized:
            observe_telegram_send("unauthorized")
            raise
        except Exception:
            observe_telegram_send("error")
            raise
