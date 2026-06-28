from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import ChatFullInfo, InlineKeyboardMarkup, MessageEntity

from app.infra.clients.telegram.interface import ITelegramBot
from app.infra.clients.telegram.settings import TelegramClientSettings


def create_bot(settings: TelegramClientSettings) -> Bot:
    if settings.proxy_url:
        session = AiohttpSession(proxy=settings.proxy_url)
        return Bot(token=settings.bot_token, session=session)
    return Bot(token=settings.bot_token)


class AiogramTelegramBot(ITelegramBot):
    """Адаптер ITelegramBot над aiogram.Bot (отправка сообщений)."""

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def get_chat(self, chat_id: int) -> ChatFullInfo:
        return await self._bot.get_chat(chat_id)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        *,
        entities: list[MessageEntity] | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text,
            entities=entities,
            reply_markup=reply_markup,
        )
