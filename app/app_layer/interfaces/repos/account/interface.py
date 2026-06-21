from abc import ABC, abstractmethod

from app.app_layer.interfaces.repos.account.dto import (
    AccountSettingsCreateDTO,
    AccountSettingsUpdateDTO,
    AccountView,
    SsauIdentityCreateDTO,
    SsauIdentityUpdateDTO,
    SsauProfileCreateDTO,
    SsauProfileUpdateDTO,
    TelegramIdentityCreateDTO,
    TelegramIdentityUpdateDTO,
)
from app.domain.entities.account.account import AccountEntity
from app.domain.entities.account.account_settings import AccountSettingsEntity
from app.domain.entities.account.ssau_identity import SsauIdentityEntity
from app.domain.entities.account.ssau_profile import SsauProfileEntity
from app.domain.entities.account.telegram_identity import TelegramIdentityEntity


class IAccountRepository(ABC):
    """Фасад персистентности аккаунта: составное чтение + гранулярная запись по частям.

    Доменного агрегата нет — координация и инварианты живут в use case'ах; этот порт лишь
    отражает, как части аккаунта лежат в БД (по таблице на часть).
    """

    # --- составное чтение ---

    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> AccountView | None:
        raise NotImplementedError

    @abstractmethod
    async def list_notifiable(self) -> list[AccountView]:
        """Аккаунты с включёнными уведомлениями, у которых есть identity и профиль."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[AccountView]:
        """Все аккаунты системы (для админских ручек)."""
        raise NotImplementedError

    # --- accounts ---

    @abstractmethod
    async def create_account(self) -> AccountEntity:
        raise NotImplementedError

    # --- telegram identity ---

    @abstractmethod
    async def create_telegram_identity(
        self, dto: TelegramIdentityCreateDTO
    ) -> TelegramIdentityEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_telegram_identity(
        self, dto: TelegramIdentityUpdateDTO
    ) -> TelegramIdentityEntity:
        raise NotImplementedError

    # --- settings ---

    @abstractmethod
    async def create_settings(self, dto: AccountSettingsCreateDTO) -> AccountSettingsEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_settings(self, dto: AccountSettingsUpdateDTO) -> AccountSettingsEntity:
        raise NotImplementedError

    # --- ssau identity ---

    @abstractmethod
    async def create_ssau_identity(self, dto: SsauIdentityCreateDTO) -> SsauIdentityEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_ssau_identity(self, dto: SsauIdentityUpdateDTO) -> SsauIdentityEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete_ssau_identity(self, account_id: int) -> None:
        """Удаляет SSAU-идентичность аккаунта (профиль удаляется каскадом)."""
        raise NotImplementedError

    # --- ssau profile ---

    @abstractmethod
    async def create_ssau_profile(self, dto: SsauProfileCreateDTO) -> SsauProfileEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_ssau_profile(self, dto: SsauProfileUpdateDTO) -> SsauProfileEntity:
        raise NotImplementedError
