from aiogram.exceptions import TelegramAPIError

try:
    from aiogram.exceptions import TelegramUnauthorized
except ImportError:  # pragma: no cover - compatibility shim
    try:
        from aiogram.exceptions import TelegramUnauthorizedError as TelegramUnauthorized
    except ImportError:
        TelegramUnauthorized = TelegramAPIError

from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.app_layer.interfaces.telegram.renderer.interface import TelegramMessageRenderer
from app.domain.messages.base import TelegramMessage
from app.infra.clients.telegram.message_sender import TelegramMessageSender
from app.infra.observability.metrics import observe_telegram_send
from app.infra.observability.telemetry import get_tracer


class TelegramNotifier(Notifier):
    def __init__(
        self,
        renderer: TelegramMessageRenderer,
        sender: TelegramMessageSender,
    ) -> None:
        self._renderer = renderer
        self._sender = sender
        self._tracer = get_tracer(__name__)

    async def send(self, chat_id: int, message: TelegramMessage) -> None:
        rendered = self._renderer.render(message)
        try:
            with self._tracer.start_as_current_span("telegram.send") as span:
                span.set_attribute("telegram.chat_id", chat_id)
                await self._sender.send(chat_id, rendered)
            observe_telegram_send("success")
        except TelegramUnauthorized:
            observe_telegram_send("unauthorized")
            raise
        except Exception:
            observe_telegram_send("error")
            raise
