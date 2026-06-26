from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramInlineKeyboardButtonDTO:
    text: str
    url: str | None = None
    callback_data: str | None = None


@dataclass(frozen=True)
class TelegramReplyMarkupDTO:
    inline_keyboard: tuple[tuple[TelegramInlineKeyboardButtonDTO, ...], ...]
