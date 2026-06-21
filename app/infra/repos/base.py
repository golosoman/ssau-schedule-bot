from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.uow.sqlalchemy_uow import get_current_session


class BaseSqlAlchemyRepository:
    """Базовый алхимический репозиторий: доступ к активной сессии UoW через
    property ``_session`` (сессию в ContextVar ставит ``SqlAlchemyUnitOfWork``)."""

    @property
    def _session(self) -> AsyncSession:
        return get_current_session()
