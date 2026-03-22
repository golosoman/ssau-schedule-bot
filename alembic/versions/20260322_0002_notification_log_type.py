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
    # Safety for reruns after a failed SQLite batch migration.
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_notification_log")

    with op.batch_alter_table("notification_log") as batch_op:
        batch_op.add_column(
            sa.Column(
                "notification_type",
                sa.String(length=32),
                nullable=True,
            )
        )
        batch_op.drop_constraint("uq_notification_once", type_="unique")
        batch_op.create_unique_constraint(
            "uq_notification_once",
            ["user_id", "lesson_id", "lesson_date", "notification_type"],
        )

    op.execute(
        "UPDATE notification_log "
        "SET notification_type = 'before_start' "
        "WHERE notification_type IS NULL"
    )

    with op.batch_alter_table("notification_log") as batch_op:
        batch_op.alter_column(
            "notification_type",
            existing_type=sa.String(length=32),
            nullable=False,
        )


def downgrade() -> None:
    # Safety for reruns after a failed SQLite batch migration.
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_notification_log")

    with op.batch_alter_table("notification_log") as batch_op:
        batch_op.drop_constraint("uq_notification_once", type_="unique")
        batch_op.drop_column("notification_type")

    # Downgrade restores the legacy unique key without notification_type.
    # Keep one record per legacy key to avoid unique violations.
    op.execute(
        "DELETE FROM notification_log "
        "WHERE id NOT IN ("
        "    SELECT MIN(id) FROM notification_log "
        "    GROUP BY user_id, lesson_id, lesson_date"
        ")"
    )

    with op.batch_alter_table("notification_log") as batch_op:
        batch_op.create_unique_constraint(
            "uq_notification_once",
            ["user_id", "lesson_id", "lesson_date"],
        )
