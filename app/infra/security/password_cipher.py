import logging

from cryptography.fernet import Fernet, InvalidToken

# Deprecated import path shim: keep exporting IPasswordCipher from this module for 1 release.
from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher

logger = logging.getLogger(__name__)


class FernetPasswordCipher(IPasswordCipher):
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


class PlaintextPasswordCipher(IPasswordCipher):
    def encrypt(self, value: str) -> str:
        return value

    def decrypt(self, value: str) -> str:
        return value
