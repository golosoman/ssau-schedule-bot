from aiogram import Router

from app.api.events.telegram.handlers.commands import (
    notifications,
    profile,
    schedule,
    system,
)

router = Router(name="telegram.commands")
router.include_router(system.router)
router.include_router(profile.router)
router.include_router(schedule.router)
router.include_router(notifications.router)

__all__ = ["router"]
