from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.rest.routers.admin.v1.messages.schemas import (
    V1SendMessageInputSchema,
    V1SendMessageOutputSchema,
)
from app.app_layer.interfaces.use_cases.send_admin_message.dto import (
    SendAdminMessageUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.send_admin_message.interface import (
    ISendAdminMessageUseCase,
)
from app.di.container import Container

router = APIRouter(prefix="/messages", tags=["Admin"])


@router.post("", response_model=V1SendMessageOutputSchema)
@inject
async def send_message(
    body: V1SendMessageInputSchema,
    use_case: Annotated[
        ISendAdminMessageUseCase,
        Depends(Provide[Container.usecases.send_admin_message_use_case]),
    ],
) -> V1SendMessageOutputSchema:
    """Отправить произвольное Telegram-сообщение списку пользователей."""
    result = await use_case.execute(
        SendAdminMessageUseCaseInputDTO(chat_ids=body.chat_ids, text=body.text)
    )
    return V1SendMessageOutputSchema.from_use_case_dto(result)
