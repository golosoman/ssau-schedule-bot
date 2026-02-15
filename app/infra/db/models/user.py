from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.ssau_profile import SsauProfile
from app.domain.entities.user import SsauCredentials, SsauUser, TelegramUser, User
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId
from app.infra.db.base import BaseTable
from app.infra.security.password_cipher import PasswordCipher


class UserModel(BaseTable):
    __tablename__ = "users"

    tg_chat_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    tg_display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    ssau_login: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ssau_password: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ssau_year_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ssau_group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ssau_group_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ssau_subgroup: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    ssau_user_type: Mapped[str] = mapped_column(String(32), nullable=False)
    academic_year_start: Mapped[date | None] = mapped_column(Date, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_domain_entity(self, password_cipher: PasswordCipher) -> User:
        credentials = None
        if self.ssau_login and self.ssau_password:
            credentials = SsauCredentials(
                login=self.ssau_login,
                password=password_cipher.decrypt(self.ssau_password),
            )

        profile = None
        if (
            self.ssau_group_id is not None
            and self.ssau_year_id is not None
            and self.academic_year_start is not None
        ):
            if self.ssau_group_name is None:
                raise ValueError("SSAU group name is missing for user.")
            profile = SsauProfile(
                group_id=GroupId(value=self.ssau_group_id),
                group_name=self.ssau_group_name,
                year_id=YearId(value=self.ssau_year_id),
                academic_year_start=self.academic_year_start,
                subgroup=Subgroup(value=self.ssau_subgroup),
                user_type=self.ssau_user_type,
            )
        return User(
            id=self.id,
            telegram=TelegramUser(
                chat_id=self.tg_chat_id,
                display_name=self.tg_display_name,
                notify_enabled=self.notify_enabled,
            ),
            ssau=SsauUser(
                credentials=credentials,
                profile=profile,
            ),
        )

    @classmethod
    def from_domain_entity(
        cls,
        user: User,
        password_cipher: PasswordCipher,
    ) -> "UserModel":
        encrypted_password = None
        if user.ssau.credentials is not None:
            encrypted_password = password_cipher.encrypt(user.ssau.credentials.password)
        profile = user.ssau.profile
        return cls(
            tg_chat_id=user.telegram.chat_id,
            tg_display_name=user.telegram.display_name,
            notify_enabled=user.telegram.notify_enabled,
            ssau_login=user.ssau.credentials.login if user.ssau.credentials else None,
            ssau_password=encrypted_password,
            ssau_year_id=profile.year_id.value if profile else None,
            ssau_group_id=profile.group_id.value if profile else None,
            ssau_group_name=profile.group_name if profile else None,
            ssau_subgroup=profile.subgroup.value if profile else 1,
            ssau_user_type=profile.user_type if profile else "student",
            academic_year_start=profile.academic_year_start if profile else None,
        )

    def apply_domain_entity(self, user: User, password_cipher: PasswordCipher) -> None:
        encrypted_password = None
        if user.ssau.credentials is not None:
            encrypted_password = password_cipher.encrypt(user.ssau.credentials.password)
        self.tg_display_name = user.telegram.display_name
        self.notify_enabled = user.telegram.notify_enabled
        self.ssau_login = user.ssau.credentials.login if user.ssau.credentials else None
        self.ssau_password = encrypted_password
        profile = user.ssau.profile
        self.ssau_year_id = profile.year_id.value if profile else None
        self.ssau_group_id = profile.group_id.value if profile else None
        self.ssau_group_name = profile.group_name if profile else None
        self.ssau_subgroup = profile.subgroup.value if profile else self.ssau_subgroup
        self.ssau_user_type = profile.user_type if profile else self.ssau_user_type
        self.academic_year_start = profile.academic_year_start if profile else None
