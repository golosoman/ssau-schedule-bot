from pydantic import BaseModel, ConfigDict, SecretStr


class ApiSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    host: str = "0.0.0.0"
    port: int = 3100
    metrics_port: int = 3103
    title: str = "SSAU Schedule Bot API"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"
    # Токен админских ручек (заголовок X-API-TOKEN). Хранится в sensitive.env.
    admin_api_token: SecretStr | None = None
