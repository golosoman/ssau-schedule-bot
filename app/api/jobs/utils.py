import logging

from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.domain.messages import ErrorMessage, TelegramMessage

logger = logging.getLogger(__name__)


async def send_alert(
    notifier: Notifier | None,
    admin_chat_id: int | None,
    message: TelegramMessage | str,
) -> None:
    if notifier is None or admin_chat_id is None:
        return
    payload = message
    if not isinstance(message, TelegramMessage):
        payload = ErrorMessage(title="Ошибка воркера", details=[message])
    try:
        await notifier.send(admin_chat_id, payload)
    except Exception:
        logger.exception("Failed to send worker alert.")
