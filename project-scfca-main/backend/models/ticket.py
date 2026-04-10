"""Ticket ORM models for SCFCA.

FR-15: All ticket types (transfer, custody_change, release, conversion, reassignment, metadata_correction).
FR-16: Ticket lifecycle — open / in_process / closed with resolution.
FR-18: Mandatory notes on approve/reject decisions.
FR-20: Ticket cancellation by handler.
FR-27: Execution linked to ticket via ticket_executions table.
SR-12: Dual approval enforcement preserved at the application layer.
SR-13: Execution traceability via ticket_executions.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.models.user import UUIDType


# --- Enum values ---

TICKET_TYPES = (
    "transfer_request",
    "custody_change",
    "release_request",
    "conversion_request",
    "reassignment",
    "metadata_correction",
)

TICKET_STATUSES = ("open", "in_process", "closed")

TICKET_RESOLUTIONS = ("pending", "approved", "rejected", "cancelled")


class Ticket(Base):
    """A custody workflow ticket requiring dual-admin approval.

    Lifecycle (FR-16): open → in_process → closed
    Resolution: pending → approved | rejected | cancelled
    """

    __tablename__ = "tickets"

    id = Column(String(8), primary_key=True)  # T-XXXX
    case_id = Column(String(8), ForeignKey("cases.id"), nullable=False, index=True)
    ticket_type = Column(
        Enum(*TICKET_TYPES, name="ticket_type_enum", native_enum=False),
        nullable=False,
    )
    description = Column(Text, nullable=False)
    status = Column(
        Enum(*TICKET_STATUSES, name="ticket_status_enum", native_enum=False),
        nullable=False,
        default="open",
    )
    resolution = Column(
        Enum(*TICKET_RESOLUTIONS, name="ticket_resolution_enum", native_enum=False),
        nullable=False,
        default="pending",
    )
    linked_doc_ids = Column(JSON, nullable=True)  # list[str]
    parameters = Column(JSON, nullable=True)  # structured params for reassignment/metadata
    created_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUIDType(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    approvals = relationship("TicketApproval", back_populates="ticket", order_by="TicketApproval.decided_at.desc()")
    execution = relationship("TicketExecution", back_populates="ticket", uselist=False)
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])

    @property
    def display_status(self) -> str:
        """Map internal lifecycle to API-compatible display status.

        Preserves backward compatibility with existing tests/frontend that
        expect: pending_review, awaiting_second_approval, approved, rejected.
        """
        if self.status == "open" and self.resolution == "pending":
            return "pending_review"
        if self.status == "in_process" and self.resolution == "pending":
            return "awaiting_second_approval"
        if self.status == "closed" and self.resolution == "approved":
            return "approved"
        if self.status == "closed" and self.resolution == "rejected":
            return "rejected"
        if self.status == "closed" and self.resolution == "cancelled":
            return "cancelled"
        return self.status


class TicketApproval(Base):
    """Individual approval or rejection decision on a ticket.

    FR-18: notes field is mandatory.
    """

    __tablename__ = "ticket_approvals"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(8), ForeignKey("tickets.id"), nullable=False, index=True)
    stage = Column(Integer, nullable=False)  # 1 or 2
    decision = Column(
        Enum("approved", "rejected", name="approval_decision_enum", native_enum=False),
        nullable=False,
    )
    decided_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=False)  # FR-18: mandatory
    decided_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="approvals")
    decider = relationship("User", foreign_keys=[decided_by])


class TicketExecution(Base):
    """Execution record for an approved ticket.

    SR-13: Links execution to originating ticket.
    FR-27: Records execution identifiers and status.
    FR-28: Records failure reason if execution fails.
    """

    __tablename__ = "ticket_executions"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(8), ForeignKey("tickets.id"), nullable=False, unique=True)
    idempotency_key = Column(String(128), nullable=False, unique=True)
    executed_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    result = Column(String(64), nullable=False)
    failure_reason = Column(Text, nullable=True)  # FR-28
    executed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="execution")
    executor = relationship("User", foreign_keys=[executed_by])
