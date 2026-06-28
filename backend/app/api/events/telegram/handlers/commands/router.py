from aiogram import Router

from app.api.events.telegram.handlers.commands.notifications import router as notifications_router
from app.api.events.telegram.handlers.commands.profile import router as profile_router
from app.api.events.telegram.handlers.commands.schedule import router as schedule_router
from app.api.events.telegram.handlers.commands.system import router as system_router

router = Router(name="telegram.commands")
router.include_router(system_router)
router.include_router(profile_router)
router.include_router(schedule_router)
router.include_router(notifications_router)
