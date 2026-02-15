from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILES = [
    "./envs/common.env",
    "./envs/local.env",
    "./envs/dev.env",
    "./envs/prod.env",
    "./envs/sensitive.env",
]

class RetrySettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    max_attempts: int = 3
    base_seconds: float = 0.5
    max_seconds: float = 5.0
    jitter_seconds: float = 0.2
    timeout_seconds: float = 15.0


class SSAUAuthSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cookie_ttl_seconds: int = 3600
    min_login_interval_seconds: int = 10


class SSAUSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    base_url: str = "https://lk.ssau.ru"
    auth: SSAUAuthSettings = Field(default_factory=SSAUAuthSettings)
    retry: RetrySettings = Field(default_factory=RetrySettings)


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: str = "sqlite+aiosqlite:///./data/ssau_schedule_bot.db"


class TelegramSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    bot_token: str
    proxy_url: str | None = None
    retry: RetrySettings = Field(default_factory=RetrySettings)


class NotificationSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    default_timezone: str = "Europe/Samara"
    lead_minutes: int = 15


class WorkerSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schedule_fetch_interval_hours: int = 12
    notification_poll_interval_seconds: int = 60


class LoggingSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    level: str = "INFO"
    format: str = "json"


class SecuritySettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fernet_key: str | None = None
    allow_plaintext: bool = False

    @model_validator(mode="after")
    def _check_cipher(self) -> "SecuritySettings":
        if not self.fernet_key and not self.allow_plaintext:
            raise ValueError(
                "SECURITY__FERNET_KEY is required or SECURITY__ALLOW_PLAINTEXT must be true."
            )
        return self


class MetricsSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000


class TelemetrySettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    enabled: bool = False
    service_name: str = "ssau-schedule-bot"
    otlp_endpoint: str | None = None


class AlertsSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    enabled: bool = False
    admin_chat_id: int | None = None


class ApiSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8080


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    ssau: SSAUSettings = Field(default_factory=SSAUSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    workers: WorkerSettings = Field(default_factory=WorkerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    metrics: MetricsSettings = Field(default_factory=MetricsSettings)
    telemetry: TelemetrySettings = Field(default_factory=TelemetrySettings)
    alerts: AlertsSettings = Field(default_factory=AlertsSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
