from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.api.jobs.notification.job import run
from app.settings.config import settings


def register(scheduler: AsyncIOScheduler) -> None:
    scheduler.add_job(
        run,
        id="notification",
        trigger=IntervalTrigger(seconds=settings.workers.notification_poll_interval_seconds),
        next_run_time=datetime.now(UTC),
        max_instances=1,
        coalesce=True,
    )
