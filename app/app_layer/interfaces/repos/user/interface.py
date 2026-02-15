from __future__ import annotations

from typing import Protocol

from app.domain.entities.user import User


class UserRepository(Protocol):
    async def get_by_chat_id(self, chat_id: int) -> User | None:
        ...

    async def upsert(self, user: User) -> User:
        ...

    async def list_enabled(self) -> list[User]:
        ...
