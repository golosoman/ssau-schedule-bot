from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.domain.entities.users.ssau_user import SsauCredentials, SsauUser
from app.domain.entities.users.telegram_user import TelegramUser


class User(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    id: int | None
    telegram: TelegramUser
    ssau: SsauUser

