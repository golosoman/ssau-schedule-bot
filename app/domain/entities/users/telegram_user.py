from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TelegramUser(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    display_name: str
    notify_enabled: bool
