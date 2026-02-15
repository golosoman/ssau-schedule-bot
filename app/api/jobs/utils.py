import logging

from app.app_layer.interfaces.notifications.notifier.interface import Notifier

logger = logging.getLogger(__name__)


async def send_alert(
    notifier: Notifier | None,
    admin_chat_id: int | None,
    message: str,
) -> None:
    if notifier is None or admin_chat_id is None:
        return
    try:
        await notifier.send(admin_chat_id, message)
    except Exception:
        logger.exception("Failed to send worker alert.")
