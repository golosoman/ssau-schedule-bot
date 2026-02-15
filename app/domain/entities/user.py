from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.domain.entities.ssau_profile import SsauProfile


class TelegramUser(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    display_name: str
    notify_enabled: bool


class SsauCredentials(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    login: str
    password: str


class SsauUser(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    credentials: SsauCredentials | None
    profile: SsauProfile | None


class User(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    id: int | None
    telegram: TelegramUser
    ssau: SsauUser
