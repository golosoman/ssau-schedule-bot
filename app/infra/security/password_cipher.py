import logging
from typing import Protocol

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class PasswordCipher(Protocol):
    def encrypt(self, value: str) -> str: ...

    def decrypt(self, value: str) -> str: ...


class FernetPasswordCipher(PasswordCipher):
    _prefix = "enc:"

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        token = self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")
        return f"{self._prefix}{token}"

    def decrypt(self, value: str) -> str:
        if not value:
            return value
        if not value.startswith(self._prefix):
            return value
        token = value[len(self._prefix) :].encode("utf-8")
        try:
            return self._fernet.decrypt(token).decode("utf-8")
        except InvalidToken:
            logger.warning("Password decrypt failed, returning empty value.")
            return ""


class PlaintextPasswordCipher(PasswordCipher):
    def encrypt(self, value: str) -> str:
        return value

    def decrypt(self, value: str) -> str:
        return value
