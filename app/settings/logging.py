from pydantic import BaseModel, ConfigDict


class LoggingSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: str = "INFO"
    format: str = "json"
