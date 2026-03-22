from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.auth import AuthSession
from app.domain.entities.lesson import Lesson
from app.domain.entities.users import SsauProfile, User


class IAuthRepository(ABC):
    @abstractmethod
    async def login(self, login: str, password: str) -> AuthSession:
        raise NotImplementedError


class IScheduleProvider(ABC):
    @abstractmethod
    async def fetch_week_schedule(self, user: User, week_number: int) -> list[Lesson]:
        raise NotImplementedError


class IScheduleRepository(ABC):
    @abstractmethod
    async def get_schedule(self, week: int) -> list[Lesson]:
        raise NotImplementedError


class ISSAUProfileProvider(ABC):
    @abstractmethod
    async def fetch_profile(self, login: str, password: str) -> SsauProfile:
        raise NotImplementedError
