from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.settings.retry import RetrySettings


class TelegramSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    bot_token: SecretStr
    proxy_url: str | None = None
    retry: RetrySettings = Field(default_factory=RetrySettings)
