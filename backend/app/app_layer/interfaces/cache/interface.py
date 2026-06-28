from abc import ABC, abstractmethod
from typing import Any


class ICacheClient(ABC):
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        *,
        nx: bool = False,
        get: bool = False,
    ) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def incr(self, key: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> int:
        raise NotImplementedError
