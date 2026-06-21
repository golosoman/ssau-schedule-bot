from app.domain.entities.base import TimestampedEntity


class AccountEntity(TimestampedEntity):
    """Корень-аккаунт: только идентичность + аудит.

    Остальные идентичности (Telegram/SSAU), настройки и профиль ссылаются на него по
    ``account_id``. Агрегатных границ не вводим — координация в use case'ах.
    """
