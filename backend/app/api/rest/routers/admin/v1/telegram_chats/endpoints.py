from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.rest.routers.admin.v1.telegram_chats.schemas import (
    V1CheckTelegramChatsInputSchema,
    V1CheckTelegramChatsOutputSchema,
)
from app.app_layer.interfaces.use_cases.check_telegram_chats.dto import (
    CheckTelegramChatsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.check_telegram_chats.interface import (
    ICheckTelegramChatsUseCase,
)
from app.di.container import Container

router = APIRouter(prefix="/telegram-chats", tags=["Admin"])


@router.post("/check", response_model=V1CheckTelegramChatsOutputSchema)
@inject
async def check_telegram_chats(
    body: V1CheckTelegramChatsInputSchema,
    use_case: Annotated[
        ICheckTelegramChatsUseCase,
        Depends(Provide[Container.usecases.check_telegram_chats_use_case]),
    ],
) -> V1CheckTelegramChatsOutputSchema:
    """Тихо проверить доступность Telegram-чатов через getChat."""
    result = await use_case.execute(CheckTelegramChatsUseCaseInputDTO(chat_ids=body.chat_ids))
    return V1CheckTelegramChatsOutputSchema.from_use_case_dto(result)
