from dataclasses import dataclass


@dataclass(frozen=True)
class ValkeyClientSettings:
    """Родные настройки клиента Valkey (маппятся из app.settings.valkey в DI)."""

    host: str
    port: int
    db: int
    password: str | None
    max_connections: int
    socket_timeout_seconds: float
    socket_connect_timeout_seconds: float
    health_check_interval_seconds: int
    retries: int
