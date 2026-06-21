from typing import TypeVar

from sqlalchemy import select

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
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher
from app.domain.entities.account.account import AccountEntity
from app.domain.entities.account.account_settings import AccountSettingsEntity
from app.domain.entities.account.ssau_identity import SsauIdentityEntity
from app.domain.entities.account.ssau_profile import SsauProfileEntity
from app.domain.entities.account.telegram_identity import TelegramIdentityEntity
from app.infra.db.models import (
    AccountModel,
    AccountSettingsModel,
    SsauIdentityModel,
    SsauProfileModel,
    TelegramIdentityModel,
)
from app.infra.repos.account.mapper import (
    account_to_entity,
    settings_to_entity,
    ssau_identity_to_entity,
    ssau_profile_to_entity,
    telegram_to_entity,
    to_account_view,
)
from app.infra.repos.base import BaseSqlAlchemyRepository

_ModelT = TypeVar("_ModelT")


class SqlAlchemyAccountRepository(BaseSqlAlchemyRepository, IAccountRepository):
    def __init__(self, password_cipher: IPasswordCipher) -> None:
        self._cipher = password_cipher

    # --- составное чтение ---

    async def get_by_chat_id(self, chat_id: int) -> AccountView | None:
        telegram = await self._session.scalar(
            select(TelegramIdentityModel).where(
                TelegramIdentityModel.telegram_chat_id == chat_id
            )
        )
        if telegram is None:
            return None
        return await self._load_view(telegram.account_id, telegram=telegram)

    async def list_notifiable(self) -> list[AccountView]:
        stmt = (
            select(
                AccountModel,
                TelegramIdentityModel,
                AccountSettingsModel,
                SsauIdentityModel,
                SsauProfileModel,
            )
            .join(TelegramIdentityModel, TelegramIdentityModel.account_id == AccountModel.id)
            .join(AccountSettingsModel, AccountSettingsModel.account_id == AccountModel.id)
            .join(SsauIdentityModel, SsauIdentityModel.account_id == AccountModel.id)
            .join(SsauProfileModel, SsauProfileModel.ssau_identity_id == SsauIdentityModel.id)
            .where(AccountSettingsModel.schedule_notifications_enabled.is_(True))
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            to_account_view(
                account=account,
                telegram=telegram,
                settings=settings,
                ssau_identity=ssau_identity,
                ssau_profile=ssau_profile,
                cipher=self._cipher,
            )
            for account, telegram, settings, ssau_identity, ssau_profile in rows
        ]

    async def list_all(self) -> list[AccountView]:
        stmt = (
            select(
                AccountModel,
                TelegramIdentityModel,
                AccountSettingsModel,
                SsauIdentityModel,
                SsauProfileModel,
            )
            .join(TelegramIdentityModel, TelegramIdentityModel.account_id == AccountModel.id)
            .join(AccountSettingsModel, AccountSettingsModel.account_id == AccountModel.id)
            .outerjoin(SsauIdentityModel, SsauIdentityModel.account_id == AccountModel.id)
            .outerjoin(SsauProfileModel, SsauProfileModel.ssau_identity_id == SsauIdentityModel.id)
            .order_by(AccountModel.id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            to_account_view(
                account=account,
                telegram=telegram,
                settings=settings,
                ssau_identity=ssau_identity,
                ssau_profile=ssau_profile,
                cipher=self._cipher,
            )
            for account, telegram, settings, ssau_identity, ssau_profile in rows
        ]

    async def _load_view(
        self,
        account_id: int,
        *,
        telegram: TelegramIdentityModel | None = None,
    ) -> AccountView:
        account = await self._session.get(AccountModel, account_id)
        if account is None:
            raise RuntimeError(f"Account {account_id} not found.")
        if telegram is None:
            telegram = await self._session.scalar(
                select(TelegramIdentityModel).where(
                    TelegramIdentityModel.account_id == account_id
                )
            )
        if telegram is None:
            raise RuntimeError(f"Telegram identity for account {account_id} not found.")
        settings = await self._session.scalar(
            select(AccountSettingsModel).where(AccountSettingsModel.account_id == account_id)
        )
        if settings is None:
            raise RuntimeError(f"Settings for account {account_id} not found.")
        ssau_identity = await self._session.scalar(
            select(SsauIdentityModel).where(SsauIdentityModel.account_id == account_id)
        )
        ssau_profile = None
        if ssau_identity is not None:
            ssau_profile = await self._session.scalar(
                select(SsauProfileModel).where(
                    SsauProfileModel.ssau_identity_id == ssau_identity.id
                )
            )
        return to_account_view(
            account=account,
            telegram=telegram,
            settings=settings,
            ssau_identity=ssau_identity,
            ssau_profile=ssau_profile,
            cipher=self._cipher,
        )

    # --- accounts ---

    async def create_account(self) -> AccountEntity:
        model = AccountModel()
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return account_to_entity(model)

    # --- telegram identity ---

    async def create_telegram_identity(
        self, dto: TelegramIdentityCreateDTO
    ) -> TelegramIdentityEntity:
        model = TelegramIdentityModel(
            account_id=dto.account_id,
            telegram_chat_id=dto.chat_id,
            telegram_display_name=dto.display_name,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return telegram_to_entity(model)

    async def update_telegram_identity(
        self, dto: TelegramIdentityUpdateDTO
    ) -> TelegramIdentityEntity:
        model = await self._require(TelegramIdentityModel, dto.id)
        model.telegram_display_name = dto.display_name
        await self._session.flush()
        await self._session.refresh(model)
        return telegram_to_entity(model)

    # --- settings ---

    async def create_settings(self, dto: AccountSettingsCreateDTO) -> AccountSettingsEntity:
        model = AccountSettingsModel(
            account_id=dto.account_id,
            schedule_notifications_enabled=dto.schedule_notifications_enabled,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return settings_to_entity(model)

    async def update_settings(self, dto: AccountSettingsUpdateDTO) -> AccountSettingsEntity:
        model = await self._require(AccountSettingsModel, dto.id)
        model.schedule_notifications_enabled = dto.schedule_notifications_enabled
        await self._session.flush()
        await self._session.refresh(model)
        return settings_to_entity(model)

    # --- ssau identity ---

    async def create_ssau_identity(self, dto: SsauIdentityCreateDTO) -> SsauIdentityEntity:
        model = SsauIdentityModel(
            account_id=dto.account_id,
            login=dto.login,
            encrypted_password=self._cipher.encrypt(dto.password),
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ssau_identity_to_entity(model, self._cipher)

    async def update_ssau_identity(self, dto: SsauIdentityUpdateDTO) -> SsauIdentityEntity:
        model = await self._require(SsauIdentityModel, dto.id)
        model.login = dto.login
        model.encrypted_password = self._cipher.encrypt(dto.password)
        await self._session.flush()
        await self._session.refresh(model)
        return ssau_identity_to_entity(model, self._cipher)

    async def delete_ssau_identity(self, account_id: int) -> None:
        identity = await self._session.scalar(
            select(SsauIdentityModel).where(SsauIdentityModel.account_id == account_id)
        )
        if identity is None:
            return
        profile = await self._session.scalar(
            select(SsauProfileModel).where(SsauProfileModel.ssau_identity_id == identity.id)
        )
        if profile is not None:
            await self._session.delete(profile)
        await self._session.delete(identity)
        await self._session.flush()

    # --- ssau profile ---

    async def create_ssau_profile(self, dto: SsauProfileCreateDTO) -> SsauProfileEntity:
        model = SsauProfileModel(
            ssau_identity_id=dto.ssau_identity_id,
            group_id=dto.group_id.value,
            year_id=dto.year_id.value,
            group_name=dto.group_name,
            academic_year_start=dto.academic_year_start,
            subgroup=str(dto.subgroup),
            user_type=dto.user_type,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ssau_profile_to_entity(model)

    async def update_ssau_profile(self, dto: SsauProfileUpdateDTO) -> SsauProfileEntity:
        model = await self._require(SsauProfileModel, dto.id)
        model.group_id = dto.group_id.value
        model.year_id = dto.year_id.value
        model.group_name = dto.group_name
        model.academic_year_start = dto.academic_year_start
        model.subgroup = str(dto.subgroup)
        model.user_type = dto.user_type
        await self._session.flush()
        await self._session.refresh(model)
        return ssau_profile_to_entity(model)

    async def _require(self, model_type: type[_ModelT], pk: int) -> _ModelT:
        model = await self._session.get(model_type, pk)
        if model is None:
            raise RuntimeError(f"{model_type.__name__} {pk} not found.")
        return model
