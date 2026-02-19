from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TelegramKeyboardBuilder:
    @staticmethod
    def conference(url: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Открыть конференцию", url=url)
        return builder.as_markup()

    @staticmethod
    def day_navigation(
        *,
        prev_callback: str,
        next_callback: str,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Предыдущий день", callback_data=prev_callback)
        builder.button(text="Следующий день", callback_data=next_callback)
        builder.adjust(2)
        return builder.as_markup()
