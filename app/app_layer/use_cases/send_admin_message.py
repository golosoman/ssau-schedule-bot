from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.use_cases.send_admin_message.dto.input import (
    SendAdminMessageUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.send_admin_message.dto.output import (
    SendAdminMessageUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.send_admin_message.interface import (
    ISendAdminMessageUseCase,
)
from app.domain.messages.plain import PlainMessage
from app.logging.config import get_logger

logger = get_logger(__name__)


class SendAdminMessageUseCase(ISendAdminMessageUseCase):
    def __init__(self, notifier: INotifier) -> None:
        self._notifier = notifier

    async def execute(
        self,
        input_dto: SendAdminMessageUseCaseInputDTO,
    ) -> SendAdminMessageUseCaseOutputDTO:
        message = PlainMessage(text=input_dto.text)
        sent: list[int] = []
        failed: list[int] = []
        for chat_id in input_dto.chat_ids:
            try:
                await self._notifier.send(chat_id, message)
                sent.append(chat_id)
            except Exception:
                logger.exception("Admin message delivery failed for chat %s.", chat_id)
                failed.append(chat_id)
        return SendAdminMessageUseCaseOutputDTO(sent=sent, failed=failed)
