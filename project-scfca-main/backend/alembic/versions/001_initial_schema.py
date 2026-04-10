"""Initial schema: users and audit_events tables.

Revision ID: 001
Revises: None
Create Date: 2026-04-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Role enum ---
    role_enum = sa.Enum("regular", "administrator", "auditor", name="role_enum")
    role_enum.create(op.get_bind(), checkfirst=True)

    # --- Users table (FR-1, FR-2, SR-4) ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- Audit events table (SR-9, SR-10, SR-11) ---
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(12), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("actor_id", sa.String(24), nullable=False, index=True),
        sa.Column("event_type", sa.String(32), nullable=False, index=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=True),
        sa.Column("entity_id", sa.String(64), nullable=True),
        sa.Column("details", JSON(), nullable=True),
        sa.Column("prev_hash", sa.String(64), nullable=True),
        sa.Column("hash", sa.String(64), nullable=False, unique=True),
    )
    op.create_index("ix_audit_events_entity", "audit_events", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("users")
    sa.Enum(name="role_enum").drop(op.get_bind(), checkfirst=True)
