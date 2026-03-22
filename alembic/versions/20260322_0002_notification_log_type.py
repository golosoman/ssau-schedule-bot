"""Add notification type to notification log.

Revision ID: 20260322_0002
Revises: 20260322_0001
Create Date: 2026-03-22

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260322_0002"
down_revision: str | None = "20260322_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("notification_log") as batch_op:
        batch_op.add_column(
            sa.Column(
                "notification_type",
                sa.String(length=32),
                nullable=False,
                server_default="before_start",
            )
        )
        batch_op.drop_constraint("uq_notification_once", type_="unique")
        batch_op.create_unique_constraint(
            "uq_notification_once",
            ["user_id", "lesson_id", "lesson_date", "notification_type"],
        )
        batch_op.alter_column("notification_type", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("notification_log") as batch_op:
        batch_op.drop_constraint("uq_notification_once", type_="unique")
        batch_op.create_unique_constraint(
            "uq_notification_once",
            ["user_id", "lesson_id", "lesson_date"],
        )
        batch_op.drop_column("notification_type")
