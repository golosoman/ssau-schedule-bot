from aiogram.exceptions import TelegramUnauthorizedError

from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.telegram.renderer.interface import ITelegramMessageRenderer
from app.app_layer.interfaces.telegram.sender.interface import (
    ITelegramMessageSender,
)
from app.domain.messages.base import TelegramMessage
from app.infra.observability.metrics.interface import IMetricsService
from app.infra.observability.telemetry.tracing import get_tracer


class TelegramNotifier(INotifier):
    def __init__(
        self,
        renderer: ITelegramMessageRenderer,
        sender: ITelegramMessageSender,
        metrics: IMetricsService,
    ) -> None:
        self._renderer = renderer
        self._sender = sender
        self._metrics = metrics
        self._tracer = get_tracer(__name__)

    async def send(self, chat_id: int, message: TelegramMessage) -> None:
        rendered = self._renderer.render(message)
        try:
            with self._tracer.start_as_current_span("telegram.send") as span:
                span.set_attribute("telegram.chat_id", chat_id)
                await self._sender.send(chat_id, rendered)
            self._metrics.observe_telegram_send("success")
        except TelegramUnauthorizedError:
            self._metrics.observe_telegram_send("unauthorized")
            raise
        except Exception:
            self._metrics.observe_telegram_send("error")
            raise
