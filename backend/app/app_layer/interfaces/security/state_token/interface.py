from abc import ABC, abstractmethod


class IStateTokenService(ABC):
    """Одноразовый подписанный токен, привязывающий веб-форму к Telegram-аккаунту."""

    @abstractmethod
    def issue(self, chat_id: int) -> str:
        """Выпустить токен для chat_id (с TTL)."""
        raise NotImplementedError

    @abstractmethod
    def verify(self, token: str) -> int:
        """Проверить токен и вернуть chat_id.

        Бросает ``InvalidStateTokenError`` / ``ExpiredStateTokenError``.
        """
        raise NotImplementedError
