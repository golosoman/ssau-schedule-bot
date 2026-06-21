from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.infra.db.session import create_session_factory, database_engine
from app.infra.db.settings import DatabaseEngineSettings
from app.infra.uow.sqlalchemy_uow import SqlAlchemyUnitOfWorkFactory
from app.settings.config import settings


class DbContainer(containers.DeclarativeContainer):
    engine: providers.Provider[AsyncEngine] = providers.Resource(
        database_engine,
        settings=providers.Singleton(
            DatabaseEngineSettings,
            url=settings.database.url,
        ),
    )
    session_factory: providers.Provider[async_sessionmaker[AsyncSession]] = providers.Singleton(
        create_session_factory,
        engine=engine,
    )
    uow_factory: providers.Provider[SqlAlchemyUnitOfWorkFactory] = providers.Singleton(
        SqlAlchemyUnitOfWorkFactory,
        session_factory=session_factory,
    )
