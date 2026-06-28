from pydantic import BaseModel, ConfigDict


class NotificationSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    default_timezone: str = "Europe/Samara"
    lead_minutes: int = 15
