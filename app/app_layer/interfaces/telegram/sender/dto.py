from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramInlineKeyboardButton:
    text: str
    url: str | None = None
    callback_data: str | None = None


@dataclass(frozen=True)
class TelegramReplyMarkup:
    inline_keyboard: tuple[tuple[TelegramInlineKeyboardButton, ...], ...]
