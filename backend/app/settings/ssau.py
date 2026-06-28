from pydantic import BaseModel, ConfigDict, Field

from app.settings.retry import RetrySettings


class SSAUAuthSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    cookie_ttl_seconds: int = 7_200
    min_login_interval_seconds: int = 10


class SSAUSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    base_url: str = "https://lk.ssau.ru"
    auth: SSAUAuthSettings = Field(default_factory=SSAUAuthSettings)
    retry: RetrySettings = Field(default_factory=RetrySettings)
