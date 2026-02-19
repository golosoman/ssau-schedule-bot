from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_layer.interfaces.repos.user.interface import UserRepository
from app.domain.entities.users import User
from app.infra.db.models import UserModel
from app.infra.security.password_cipher import PasswordCipher


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession, password_cipher: PasswordCipher) -> None:
        self._session = session
        self._password_cipher = password_cipher

    async def get_by_chat_id(self, chat_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.tg_chat_id == chat_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_domain_entity(self._password_cipher)

    async def upsert(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.tg_chat_id == user.telegram.chat_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = UserModel.from_domain_entity(user, self._password_cipher)
            self._session.add(model)
        else:
            model.apply_domain_entity(user, self._password_cipher)

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain_entity(self._password_cipher)

    async def list_enabled(self) -> list[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.notify_enabled.is_(True))
        )
        return [model.to_domain_entity(self._password_cipher) for model in result.scalars().all()]
