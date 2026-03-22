from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.users import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def list_enabled(self) -> list[User]:
        raise NotImplementedError
