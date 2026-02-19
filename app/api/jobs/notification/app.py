from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.api.jobs.notification.job import run
from app.settings.config import Settings


def register(scheduler: AsyncIOScheduler, settings: Settings) -> None:
    scheduler.add_job(
        run,
        id="notification",
        trigger=IntervalTrigger(seconds=settings.workers.notification_poll_interval_seconds),
        next_run_time=datetime.now(timezone.utc),
        max_instances=1,
        coalesce=True,
    )
