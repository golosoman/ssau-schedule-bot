from pydantic import BaseModel, ConfigDict


class AlertsSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    admin_chat_id: int | None = None
