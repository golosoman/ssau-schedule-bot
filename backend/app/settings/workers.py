from pydantic import BaseModel, ConfigDict


class WorkerSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    schedule_fetch_interval_hours: int = 12
    notification_poll_interval_seconds: int = 60
    metrics_port: int = 3102
