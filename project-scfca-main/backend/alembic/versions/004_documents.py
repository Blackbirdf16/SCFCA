"""Documents table.

Revision ID: 004
Revises: 003
Create Date: 2026-04-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(8), primary_key=True),
        sa.Column("filename", sa.String(256), nullable=False),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("sha256_hex", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(8), sa.ForeignKey("cases.id"), nullable=True, index=True),
        sa.Column("ticket_id", sa.String(8), sa.ForeignKey("tickets.id"), nullable=True, index=True),
        sa.Column("uploaded_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("documents")
