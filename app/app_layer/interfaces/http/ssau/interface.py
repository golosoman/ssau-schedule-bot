from __future__ import annotations

from typing import Protocol

from app.domain.entities.auth import AuthSession
from app.domain.entities.lesson import Lesson
from app.domain.entities.ssau_profile import SsauProfile
from app.domain.entities.user import User


class AuthRepository(Protocol):
    async def login(self, login: str, password: str) -> AuthSession:
        ...


class ScheduleProvider(Protocol):
    async def fetch_week_schedule(self, user: User, week_number: int) -> list[Lesson]:
        ...


class ScheduleRepository(Protocol):
    async def get_schedule(self, week: int) -> list[Lesson]:
        ...


class SSAUProfileProvider(Protocol):
    async def fetch_profile(self, login: str, password: str) -> SsauProfile:
        ...
