from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class IUnitOfWork(ABC):
    """Transactional boundary.

    Repositories are injected separately and use the active session from the
    current UoW context. UoW must not expose repository properties.
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
