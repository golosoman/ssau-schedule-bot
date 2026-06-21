from contextvars import ContextVar, Token
from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork

_session_ctx: ContextVar[AsyncSession | None] = ContextVar(
    "sqlalchemy_uow_session",
    default=None,
)


class SessionNotFoundError(RuntimeError):
    pass


class NestedUnitOfWorkError(RuntimeError):
    pass


def get_current_session() -> AsyncSession:
    session = _session_ctx.get()
    if session is None:
        raise SessionNotFoundError("Repository call requires an active Unit of Work.")
    return session


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._session_token: Token[AsyncSession | None] | None = None
        self._committed = False

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        if _session_ctx.get() is not None:
            raise NestedUnitOfWorkError("Nested Unit of Work is not allowed.")
        self._session = self._session_factory()
        self._session_token = _session_ctx.set(self._session)
        self._committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc:
                await self.rollback()
            elif not self._committed:
                await self.commit()
        finally:
            await self._session.close()
            self._session = None
            if self._session_token is not None:
                _session_ctx.reset(self._session_token)
                self._session_token = None

    async def commit(self) -> None:
        if self._session is None:
            return
        try:
            await self._session.commit()
        except SQLAlchemyError:
            await self._session.rollback()
            raise
        self._committed = True

    async def rollback(self) -> None:
        if self._session is None:
            return
        await self._session.rollback()
        self._committed = True


class SqlAlchemyUnitOfWorkFactory:
    """Создаёт UoW синхронно. Резолвится в DI один раз (с уже инициализированным
    engine), а вызов фабрики не трогает DI — поэтому `async with uow_factory()`
    работает в use case'ах и job'ах."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    def __call__(self) -> IUnitOfWork:
        return SqlAlchemyUnitOfWork(self._session_factory)
