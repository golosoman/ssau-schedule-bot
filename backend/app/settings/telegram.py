from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.settings.retry import RetrySettings


class TelegramSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    bot_token: SecretStr
    proxy_url: str | None = None
    metrics_port: int = 3101
    # Страница авторизации фронта — бот шлёт сюда ссылку из /auth (?token=…).
    frontend_auth_url: str = "http://localhost:5173/auth"
    retry: RetrySettings = Field(default_factory=RetrySettings)
