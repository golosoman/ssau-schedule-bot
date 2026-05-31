from pydantic import BaseModel, ConfigDict


class MetricsSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
