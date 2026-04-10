"""Cases, assets, frozen valuations, assignment history tables.

Revision ID: 002
Revises: 001
Create Date: 2026-04-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Cases table (FR-5, SR-17) ---
    op.create_table(
        "cases",
        sa.Column("id", sa.String(8), primary_key=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("wallet_ref", sa.String(64), nullable=False),
        sa.Column("handler_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("custody_status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
    )

    # --- Case assignment history (FR-9) ---
    op.create_table(
        "case_assignment_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(8), sa.ForeignKey("cases.id"), nullable=False, index=True),
        sa.Column("from_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("to_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ticket_id", sa.String(8), nullable=True),
        sa.Column("assigned_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- Assets table (FR-10, FR-12, SR-15) ---
    op.create_table(
        "assets",
        sa.Column("id", sa.String(8), primary_key=True),
        sa.Column("case_id", sa.String(8), sa.ForeignKey("cases.id"), nullable=False, index=True),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("asset_type", sa.String(32), nullable=False),
        sa.Column("quantity", sa.Numeric(28, 8), nullable=False),
        sa.Column("protocol", sa.String(32), nullable=True),
        sa.Column("network", sa.String(32), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="registered"),
        sa.Column("notes", sa.String(512), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("registered_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
    )

    # --- Frozen valuations table (FR-11) ---
    op.create_table(
        "frozen_valuations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("asset_id", sa.String(8), sa.ForeignKey("assets.id"), nullable=False, index=True),
        sa.Column("reference_currency", sa.String(8), nullable=False, server_default="USDT"),
        sa.Column("value", sa.Numeric(28, 8), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("frozen_valuations")
    op.drop_table("assets")
    op.drop_table("case_assignment_history")
    op.drop_table("cases")
