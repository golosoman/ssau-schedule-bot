from fastapi import APIRouter

from app.api.rest.routers.admin.v1.messages.endpoints import router as messages_router
from app.api.rest.routers.admin.v1.telegram_chats.endpoints import (
    router as telegram_chats_router,
)
from app.api.rest.routers.admin.v1.users.endpoints import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(users_router)
router.include_router(messages_router)
router.include_router(telegram_chats_router)
