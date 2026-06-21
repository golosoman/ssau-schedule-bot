from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.settings.retry import RetrySettings


class TelegramSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    bot_token: SecretStr
    proxy_url: str | None = None
    metrics_port: int = 3101
    retry: RetrySettings = Field(default_factory=RetrySettings)
