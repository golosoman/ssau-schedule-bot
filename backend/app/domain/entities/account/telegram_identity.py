from app.domain.entities.base import TimestampedEntity


class TelegramIdentityEntity(TimestampedEntity):
    """Telegram-идентичность аккаунта (якорь: по ``chat_id`` узнаём пользователя)."""

    account_id: int
    chat_id: int
    display_name: str
