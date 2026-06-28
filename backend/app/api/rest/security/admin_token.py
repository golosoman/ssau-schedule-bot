import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.settings.config import settings

_admin_token_header = APIKeyHeader(name="X-API-TOKEN", auto_error=False)


async def require_admin_token(token: str | None = Depends(_admin_token_header)) -> None:
    """Авторизация админских ручек по заголовку ``X-API-TOKEN`` (fail-closed)."""
    configured = settings.api.admin_api_token
    if configured is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API token is not configured.",
        )
    if token is None or not secrets.compare_digest(token, configured.get_secret_value()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-TOKEN.",
        )
