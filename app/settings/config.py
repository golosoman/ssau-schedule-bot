from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.alerts import AlertsSettings
from app.settings.api import ApiSettings
from app.settings.database import DatabaseSettings
from app.settings.logging import LoggingSettings
from app.settings.metrics import MetricsSettings
from app.settings.notifications import NotificationSettings
from app.settings.security import SecuritySettings
from app.settings.ssau import SSAUSettings
from app.settings.telegram import TelegramSettings
from app.settings.telemetry import TelemetrySettings
from app.settings.workers import WorkerSettings

ENVS_DIR = "./envs"
ENV = os.getenv("ENV", "local")
ENV_FILES = (
    f"{ENVS_DIR}/sensitive.env",
    f"{ENVS_DIR}/common.env",
    f"{ENVS_DIR}/{ENV}.env",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        frozen=True,
    )

    # Required zones: no default — fail fast on startup if not configured.
    telegram: TelegramSettings
    security: SecuritySettings

    # Optional zones: fully defaulted.
    ssau: SSAUSettings = SSAUSettings()
    database: DatabaseSettings = DatabaseSettings()
    notifications: NotificationSettings = NotificationSettings()
    workers: WorkerSettings = WorkerSettings()
    logging: LoggingSettings = LoggingSettings()
    metrics: MetricsSettings = MetricsSettings()
    telemetry: TelemetrySettings = TelemetrySettings()
    alerts: AlertsSettings = AlertsSettings()
    api: ApiSettings = ApiSettings()


@lru_cache
def get_settings() -> Settings:
    # Required zones (telegram, security) are populated from the environment,
    # which mypy cannot see — hence the call-arg ignore.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
