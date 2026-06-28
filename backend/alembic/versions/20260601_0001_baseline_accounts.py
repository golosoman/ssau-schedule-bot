"""Baseline account-centric schema.

Revision ID: 20260601_0001
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260601_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _id_column() -> sa.Column[int]:
    return sa.Column(
        "id",
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        primary_key=True,
        autoincrement=True,
    )


def _created_at() -> sa.Column[object]:
    return sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)


def _updated_at() -> sa.Column[object]:
    return sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "accounts",
        _id_column(),
        _created_at(),
        _updated_at(),
    )

    op.create_table(
        "account_telegram_identities",
        _id_column(),
        _created_at(),
        _updated_at(),
        sa.Column(
            "account_id",
            sa.BigInteger(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_display_name", sa.String(length=128), nullable=False),
    )
    op.create_index(
        "ix_account_telegram_identities_telegram_chat_id",
        "account_telegram_identities",
        ["telegram_chat_id"],
        unique=True,
    )

    op.create_table(
        "account_settings",
        _id_column(),
        _created_at(),
        _updated_at(),
        sa.Column(
            "account_id",
            sa.BigInteger(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("schedule_notifications_enabled", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "account_ssau_identities",
        _id_column(),
        _created_at(),
        _updated_at(),
        sa.Column(
            "account_id",
            sa.BigInteger(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("login", sa.String(length=64), nullable=False),
        sa.Column("encrypted_password", sa.String(length=512), nullable=False),
    )

    op.create_table(
        "account_ssau_profiles",
        _id_column(),
        _created_at(),
        _updated_at(),
        sa.Column(
            "ssau_identity_id",
            sa.BigInteger(),
            sa.ForeignKey("account_ssau_identities.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("year_id", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=128), nullable=False),
        sa.Column("academic_year_start", sa.Date(), nullable=False),
        sa.Column("subgroup", sa.String(length=16), nullable=False),
        sa.Column("user_type", sa.String(length=32), nullable=False),
    )

    op.create_table(
        "notification_log",
        _id_column(),
        _created_at(),
        sa.Column(
            "account_id",
            sa.BigInteger(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("lesson_id", sa.BigInteger(), nullable=False),
        sa.Column("lesson_date", sa.Date(), nullable=False),
        sa.Column("notification_type", sa.String(length=32), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "account_id",
            "lesson_id",
            "lesson_date",
            "notification_type",
            name="uq_notification_once",
        ),
    )
    op.create_index("ix_notification_log_account_id", "notification_log", ["account_id"])


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_table("account_ssau_profiles")
    op.drop_table("account_ssau_identities")
    op.drop_table("account_settings")
    op.drop_table("account_telegram_identities")
    op.drop_table("accounts")
