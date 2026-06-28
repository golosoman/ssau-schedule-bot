from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher
from app.domain.entities.account.account import AccountEntity
from app.domain.entities.account.account_settings import AccountSettingsEntity
from app.domain.entities.account.ssau_identity import SsauIdentityEntity
from app.domain.entities.account.ssau_profile import SsauProfileEntity
from app.domain.entities.account.telegram_identity import TelegramIdentityEntity
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId
from app.infra.db.models import (
    AccountModel,
    AccountSettingsModel,
    SsauIdentityModel,
    SsauProfileModel,
    TelegramIdentityModel,
)


def account_to_entity(model: AccountModel) -> AccountEntity:
    return AccountEntity(id=model.id, created_at=model.created_at, updated_at=model.updated_at)


def telegram_to_entity(model: TelegramIdentityModel) -> TelegramIdentityEntity:
    return TelegramIdentityEntity(
        id=model.id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        account_id=model.account_id,
        chat_id=model.telegram_chat_id,
        display_name=model.telegram_display_name,
    )


def settings_to_entity(model: AccountSettingsModel) -> AccountSettingsEntity:
    return AccountSettingsEntity(
        id=model.id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        account_id=model.account_id,
        schedule_notifications_enabled=model.schedule_notifications_enabled,
    )


def ssau_identity_to_entity(
    model: SsauIdentityModel, cipher: IPasswordCipher
) -> SsauIdentityEntity:
    return SsauIdentityEntity(
        id=model.id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        account_id=model.account_id,
        login=model.login,
        password=cipher.decrypt(model.encrypted_password),
    )


def ssau_profile_to_entity(model: SsauProfileModel) -> SsauProfileEntity:
    return SsauProfileEntity(
        id=model.id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        ssau_identity_id=model.ssau_identity_id,
        group_id=GroupId(value=model.group_id),
        year_id=YearId(value=model.year_id),
        group_name=model.group_name,
        academic_year_start=model.academic_year_start,
        subgroup=Subgroup.parse(model.subgroup),
        user_type=model.user_type,
    )


def to_account_view(
    *,
    account: AccountModel,
    telegram: TelegramIdentityModel,
    settings: AccountSettingsModel,
    ssau_identity: SsauIdentityModel | None,
    ssau_profile: SsauProfileModel | None,
    cipher: IPasswordCipher,
) -> AccountViewDTO:
    return AccountViewDTO(
        account=account_to_entity(account),
        telegram=telegram_to_entity(telegram),
        settings=settings_to_entity(settings),
        ssau_identity=(
            ssau_identity_to_entity(ssau_identity, cipher) if ssau_identity is not None else None
        ),
        ssau_profile=(ssau_profile_to_entity(ssau_profile) if ssau_profile is not None else None),
    )
