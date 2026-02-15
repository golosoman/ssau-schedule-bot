from aiogram import Router

from app.api.events.telegram.handlers.commands import router as commands_router

router = Router(name="telegram")
router.include_router(commands_router)

__all__ = ["router"]
