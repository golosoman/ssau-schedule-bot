from pydantic import BaseModel, ConfigDict, SecretStr


class ApiSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    host: str = "0.0.0.0"
    port: int = 3100
    metrics_port: int = 3103
    # Разрешённые origin'ы фронтенда (CORS). Задаётся per-env: в проде — домен фронта.
    # Из env: API__CORS_ORIGINS='["https://auth.sasau.ru"]'.
    cors_origins: list[str] = ["http://localhost:5173"]
    title: str = "SSAU Schedule Bot API"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"
    # Токен админских ручек (заголовок X-API-TOKEN). Хранится в sensitive.env.
    admin_api_token: SecretStr | None = None
