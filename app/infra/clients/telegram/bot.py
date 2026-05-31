from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from app.infra.clients.telegram.settings import TelegramClientSettings


def create_bot(settings: TelegramClientSettings) -> Bot:
    if settings.proxy_url:
        session = AiohttpSession(proxy=settings.proxy_url)
        return Bot(token=settings.bot_token, session=session)
    return Bot(token=settings.bot_token)
