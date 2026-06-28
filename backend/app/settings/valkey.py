from pydantic import BaseModel, ConfigDict, SecretStr


class ValkeySettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0
    password: SecretStr | None = None

    # Пул и таймауты (production-ready клиент).
    max_connections: int = 10
    socket_timeout_seconds: float = 5.0
    socket_connect_timeout_seconds: float = 5.0
    health_check_interval_seconds: int = 30
    retries: int = 3
