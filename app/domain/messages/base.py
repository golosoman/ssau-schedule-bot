from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TelegramMessage(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)
