from fastapi import HTTPException, status

from app.app_layer.interfaces.security.state_token.errors import (
    BaseStateTokenError,
    ExpiredStateTokenError,
)
from app.app_layer.interfaces.security.state_token.interface import IStateTokenService


def verify_state_token(service: IStateTokenService, token: str) -> int:
    """Проверяет state-токен авторизации и возвращает chat_id, маппя доменные
    ошибки токена в HTTP-ответы (410 — протух, 401 — невалиден/подделан)."""
    try:
        return service.verify(token)
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
