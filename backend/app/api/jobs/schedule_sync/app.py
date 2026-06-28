from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.api.jobs.schedule_sync.job import run
from app.settings.config import settings


def register(scheduler: AsyncIOScheduler) -> None:
    scheduler.add_job(
        run,
        id="schedule_sync",
        trigger=IntervalTrigger(hours=settings.workers.schedule_fetch_interval_hours),
        next_run_time=datetime.now(UTC),
        max_instances=1,
        coalesce=True,
    )
