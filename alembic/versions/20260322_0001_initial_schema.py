"""Initial schema.

Revision ID: 20260322_0001
Revises:
Create Date: 2026-03-22

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260322_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _id_type() -> sa.TypeEngine:
    return sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("tg_chat_id", sa.Integer(), nullable=False),
        sa.Column("tg_display_name", sa.String(length=128), nullable=False),
        sa.Column("notify_enabled", sa.Boolean(), nullable=False),
        sa.Column("ssau_login", sa.String(length=64), nullable=True),
        sa.Column("ssau_password", sa.String(length=512), nullable=True),
        sa.Column("ssau_year_id", sa.Integer(), nullable=True),
        sa.Column("ssau_group_id", sa.Integer(), nullable=True),
        sa.Column("ssau_group_name", sa.String(length=128), nullable=True),
        sa.Column("ssau_subgroup", sa.Integer(), nullable=False),
        sa.Column("ssau_user_type", sa.String(length=32), nullable=False),
        sa.Column("academic_year_start", sa.Date(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_tg_chat_id", "users", ["tg_chat_id"], unique=True)

    op.create_table(
        "schedule_cache",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lessons_json", sa.JSON(), nullable=False),
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "week_number", name="uq_schedule_cache_user_week"),
    )
    op.create_index("ix_schedule_cache_user_id", "schedule_cache", ["user_id"], unique=False)

    op.create_table(
        "notification_log",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("lesson_date", sa.Date(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "lesson_id",
            "lesson_date",
            name="uq_notification_once",
        ),
    )
    op.create_index("ix_notification_log_user_id", "notification_log", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notification_log_user_id", table_name="notification_log")
    op.drop_table("notification_log")

    op.drop_index("ix_schedule_cache_user_id", table_name="schedule_cache")
    op.drop_table("schedule_cache")

    op.drop_index("ix_users_tg_chat_id", table_name="users")
    op.drop_table("users")
