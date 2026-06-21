from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.entities.account.account import AccountEntity
from app.domain.entities.account.account_settings import AccountSettingsEntity
from app.domain.entities.account.ssau_identity import SsauIdentityEntity
from app.domain.entities.account.ssau_profile import SsauProfileEntity
from app.domain.entities.account.telegram_identity import TelegramIdentityEntity
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId


class AccountView(BaseModel):
    """Составное чтение аккаунта: корень + идентичности + настройки (+ профиль)."""

    model_config = ConfigDict(frozen=True)

    account: AccountEntity
    telegram: TelegramIdentityEntity
    settings: AccountSettingsEntity
    ssau_identity: SsauIdentityEntity | None
    ssau_profile: SsauProfileEntity | None

    @property
    def account_id(self) -> int:
        return self.account.id

    @property
    def chat_id(self) -> int:
        return self.telegram.chat_id

    @property
    def is_authed(self) -> bool:
        return self.ssau_identity is not None

    @property
    def is_provisioned(self) -> bool:
        return self.ssau_profile is not None


# --- Save-DTO: create (без id) / update (с id) ---


class TelegramIdentityCreateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account_id: int
    chat_id: int
    display_name: str


class TelegramIdentityUpdateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    display_name: str


class AccountSettingsCreateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account_id: int
    schedule_notifications_enabled: bool


class AccountSettingsUpdateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    schedule_notifications_enabled: bool


class SsauIdentityCreateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account_id: int
    login: str
    password: str


class SsauIdentityUpdateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    login: str
    password: str


class SsauProfileCreateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    ssau_identity_id: int
    group_id: GroupId
    year_id: YearId
    group_name: str
    academic_year_start: date
    subgroup: Subgroup
    user_type: str


class SsauProfileUpdateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    group_id: GroupId
    year_id: YearId
    group_name: str
    academic_year_start: date
    subgroup: Subgroup
    user_type: str
