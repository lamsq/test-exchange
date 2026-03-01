"""
responses table
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("result", sa.String(length=32), nullable=False),
        sa.Column("time_last_update_unix", sa.BigInteger(), nullable=False),
        sa.Column("base_code", sa.String(length=16), nullable=False),
        sa.Column("conversion_rates", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("responses")
