from app.domain.messages.base import TelegramMessage


class InfoMessage(TelegramMessage):
    title: str
    lines: list[str]
