from pydantic import BaseModel, ConfigDict


class RetrySettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_attempts: int = 3
    base_seconds: float = 0.5
    max_seconds: float = 5.0
    jitter_seconds: float = 0.2
    timeout_seconds: float = 15.0
