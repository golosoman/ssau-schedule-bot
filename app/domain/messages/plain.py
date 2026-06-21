from app.domain.messages.base import TelegramMessage


class PlainMessage(TelegramMessage):
    """Произвольный текст без форматирования (напр. админская рассылка)."""

    text: str
