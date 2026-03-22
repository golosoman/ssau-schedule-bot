from __future__ import annotations

from abc import ABC, abstractmethod


class IPasswordCipher(ABC):
    @abstractmethod
    def encrypt(self, value: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, value: str) -> str:
        raise NotImplementedError
