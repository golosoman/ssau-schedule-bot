from __future__ import annotations

from datetime import date

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select

from app.domain.constants import DEFAULT_SUBGROUP_VALUE
from app.domain.entities.users import (
    SsauCredentials,
    SsauProfile,
    SsauProfileDetails,
    SsauProfileIds,
    SsauUser,
    TelegramUser,
    User,
)
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId
from app.infra.db import create_engine, create_session_factory
from app.infra.db import models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models import UserModel
from app.infra.security.password_cipher import FernetPasswordCipher
from app.infra.uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_sqlite_uow_persists_user(tmp_path) -> None:
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite+aiosqlite:///{db_path}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = create_session_factory(engine)
    cipher = FernetPasswordCipher(Fernet.generate_key().decode())

    user = User(
        id=None,
        telegram=TelegramUser(
            chat_id=100,
            display_name="tester",
            notify_enabled=True,
        ),
        ssau=SsauUser(
            credentials=SsauCredentials(login="login", password="secret"),
            profile=SsauProfile(
                profile_ids=SsauProfileIds(
                    group_id=GroupId(value=755932538),
                    year_id=YearId(value=14),
                ),
                profile_details=SsauProfileDetails(
                    group_name="Test",
                    academic_year_start=date(2025, 9, 1),
                    subgroup=Subgroup(value=DEFAULT_SUBGROUP_VALUE),
                    user_type="student",
                ),
            ),
        ),
    )

    async with SqlAlchemyUnitOfWork(session_factory, cipher) as uow:
        await uow.users.upsert(user)

    async with SqlAlchemyUnitOfWork(session_factory, cipher) as uow:
        loaded = await uow.users.get_by_chat_id(100)

    assert loaded is not None
    assert loaded.ssau.credentials is not None
    assert loaded.ssau.credentials.password == "secret"
    assert loaded.ssau.profile is not None
    assert int(loaded.ssau.profile.profile_ids.group_id) == 755932538

    async with session_factory() as session:
        result = await session.execute(select(UserModel).where(UserModel.tg_chat_id == 100))
        model = result.scalar_one()
        assert model.ssau_password.startswith("enc:")

    await engine.dispose()
