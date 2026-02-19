from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_layer.interfaces.repos.schedule_cache.interface import (
    ScheduleCacheRepository,
)
from app.domain.entities.schedule_cache import ScheduleCache
from app.infra.db.models import ScheduleCacheModel


class SqlAlchemyScheduleCacheRepository(ScheduleCacheRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, user_id: int, week_number: int) -> ScheduleCache | None:
        result = await self._session.execute(
            select(ScheduleCacheModel).where(
                ScheduleCacheModel.user_id == user_id,
                ScheduleCacheModel.week_number == week_number,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_domain_entity()

    async def upsert(self, cache: ScheduleCache) -> None:
        result = await self._session.execute(
            select(ScheduleCacheModel).where(
                ScheduleCacheModel.user_id == cache.user_id,
                ScheduleCacheModel.week_number == cache.week_number,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = ScheduleCacheModel.from_domain_entity(cache)
            self._session.add(model)
        else:
            model.apply_domain_entity(cache)

        await self._session.flush()
