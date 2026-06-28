from pydantic import BaseModel, ConfigDict


class TelemetrySettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    service_name: str = "ssau-schedule-bot"
    otlp_endpoint: str | None = None
