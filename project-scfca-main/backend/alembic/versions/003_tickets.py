"""Tickets, ticket approvals, and ticket executions tables.

Revision ID: 003
Revises: 002
Create Date: 2026-04-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Tickets table (FR-15, FR-16) ---
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(8), primary_key=True),
        sa.Column("case_id", sa.String(8), sa.ForeignKey("cases.id"), nullable=False, index=True),
        sa.Column("ticket_type", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolution", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("linked_doc_ids", sa.JSON(), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_to", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- Ticket approvals table (FR-18) ---
    op.create_table(
        "ticket_approvals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(8), sa.ForeignKey("tickets.id"), nullable=False, index=True),
        sa.Column("stage", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(10), nullable=False),
        sa.Column("decided_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- Ticket executions table (SR-13, FR-27) ---
    op.create_table(
        "ticket_executions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(8), sa.ForeignKey("tickets.id"), nullable=False, unique=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("executed_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("result", sa.String(64), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ticket_executions")
    op.drop_table("ticket_approvals")
    op.drop_table("tickets")
