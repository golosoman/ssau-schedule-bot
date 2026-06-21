from datetime import date

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select

from app.app_layer.interfaces.repos.account.dto import (
    AccountSettingsCreateDTO,
    SsauIdentityCreateDTO,
    SsauProfileCreateDTO,
    TelegramIdentityCreateDTO,
)
from app.domain.constants import DEFAULT_SUBGROUP_VALUE
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId
from app.infra.db import models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models import SsauIdentityModel
from app.infra.db.session import create_engine, create_session_factory
from app.infra.db.settings import DatabaseEngineSettings
from app.infra.repos.account.repo import SqlAlchemyAccountRepository
from app.infra.security.password_cipher import FernetPasswordCipher
from app.infra.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_sqlite_account_repository_roundtrip(tmp_path) -> None:
    db_path = tmp_path / "test.db"
    engine = create_engine(DatabaseEngineSettings(url=f"sqlite+aiosqlite:///{db_path}"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = create_session_factory(engine)
    cipher = FernetPasswordCipher(Fernet.generate_key().decode())
    account_repo = SqlAlchemyAccountRepository(cipher)

    async with SqlAlchemyUnitOfWork(session_factory):
        account = await account_repo.create_account()
        await account_repo.create_telegram_identity(
            TelegramIdentityCreateDTO(
                account_id=account.id, chat_id=100, display_name="tester"
            )
        )
        await account_repo.create_settings(
            AccountSettingsCreateDTO(
                account_id=account.id, schedule_notifications_enabled=True
            )
        )
        identity = await account_repo.create_ssau_identity(
            SsauIdentityCreateDTO(account_id=account.id, login="login", password="secret")
        )
        await account_repo.create_ssau_profile(
            SsauProfileCreateDTO(
                ssau_identity_id=identity.id,
                group_id=GroupId(value=755932538),
                year_id=YearId(value=14),
                group_name="Test",
                academic_year_start=date(2025, 9, 1),
                subgroup=Subgroup(value=DEFAULT_SUBGROUP_VALUE),
                user_type="student",
            )
        )

    async with SqlAlchemyUnitOfWork(session_factory):
        view = await account_repo.get_by_chat_id(100)
        notifiable = await account_repo.list_notifiable()

    assert view is not None
    assert view.is_authed
    assert view.is_provisioned
    assert view.ssau_identity is not None
    assert view.ssau_identity.password == "secret"
    assert view.ssau_profile is not None
    assert view.ssau_profile.group_id.value == 755932538
    assert [v.account_id for v in notifiable] == [view.account_id]

    async with session_factory() as session:
        result = await session.execute(
            select(SsauIdentityModel).where(SsauIdentityModel.account_id == view.account_id)
        )
        model = result.scalar_one()
        assert model.encrypted_password.startswith("enc:")

    await engine.dispose()
