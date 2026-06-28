class BaseStateTokenError(Exception):
    """Базовая ошибка state-токена авторизации."""


class InvalidStateTokenError(BaseStateTokenError):
    """Токен повреждён, подделан или имеет неверный формат."""


class ExpiredStateTokenError(BaseStateTokenError):
    """Срок действия токена истёк."""
