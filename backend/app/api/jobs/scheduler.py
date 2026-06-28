from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.api.jobs.notification.app import register as register_notifications
from app.api.jobs.schedule_sync.app import register as register_schedule_sync
from app.settings.config import settings


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(
        timezone=ZoneInfo(settings.notifications.default_timezone),
        job_defaults={
            "max_instances": 1,
            "coalesce": True,
            "misfire_grace_time": 60,
        },
    )
    register_schedule_sync(scheduler)
    register_notifications(scheduler)
    return scheduler
