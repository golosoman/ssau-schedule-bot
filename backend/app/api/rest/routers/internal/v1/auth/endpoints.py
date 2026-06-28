from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.rest.routers.internal.v1.auth.schemas import (
    V1AuthSsauInputSchema,
    V1AuthSsauOutputSchema,
)
from app.app_layer.interfaces.security.state_token.errors import (
    BaseStateTokenError,
    ExpiredStateTokenError,
)
from app.app_layer.interfaces.security.state_token.interface import IStateTokenService
from app.app_layer.interfaces.use_cases.authenticate_user.dto import (
    AuthenticateUserUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.authenticate_user.interface import (
    IAuthenticateUserUseCase,
)
from app.di.container import Container

router = APIRouter(prefix="/auth", tags=["Internal"])


@router.post("/ssau", response_model=V1AuthSsauOutputSchema)
@inject
async def authenticate_ssau(
    body: V1AuthSsauInputSchema,
    state_token_service: Annotated[
        IStateTokenService, Depends(Provide[Container.core.state_token_service])
    ],
    authenticate_use_case: Annotated[
        IAuthenticateUserUseCase,
        Depends(Provide[Container.usecases.authenticate_user_use_case]),
    ],
) -> V1AuthSsauOutputSchema:
    """Авторизация СНИУ с веб-страницы: проверяем state-токен (привязка к Telegram),
    сохраняем доступ и подтягиваем профиль через ``AuthenticateUserUseCase``."""
    try:
        chat_id = state_token_service.verify(body.token)
    except ExpiredStateTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Ссылка устарела. Запроси новую в боте: /auth",
        ) from exc
    except BaseStateTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительная ссылка авторизации.",
        ) from exc

    result = await authenticate_use_case.execute(
        AuthenticateUserUseCaseInputDTO(chat_id=chat_id, login=body.login, password=body.password)
    )
    profile = result.account.ssau_profile
    return V1AuthSsauOutputSchema(
        status=result.status,
        group_name=profile.group_name if profile is not None else None,
    )
