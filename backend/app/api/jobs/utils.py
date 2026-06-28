from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.domain.messages.base import TelegramMessage
from app.domain.messages.error import ErrorMessage
from app.logging.config import get_logger

logger = get_logger(__name__)


async def send_alert(
    notifier: INotifier | None,
    admin_chat_id: int | None,
    message: TelegramMessage | str,
) -> None:
    if notifier is None or admin_chat_id is None:
        return
    if isinstance(message, TelegramMessage):
        payload: TelegramMessage = message
    else:
        payload = ErrorMessage(title="Ошибка воркера", details=[message])
    try:
        await notifier.send(admin_chat_id, payload)
    except Exception:
        logger.exception("Failed to send worker alert.")
