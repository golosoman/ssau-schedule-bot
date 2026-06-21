from abc import ABC, abstractmethod

from app.domain.entities.auth import AuthSession


class ISsauAuthClient(ABC):
    """Контракт SSAU auth-клиента: логин по логину/паролю."""

    @abstractmethod
    async def login(self, login: str, password: str) -> AuthSession:
        raise NotImplementedError
