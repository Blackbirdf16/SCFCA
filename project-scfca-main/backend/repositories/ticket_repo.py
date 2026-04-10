"""Ticket repository — data access for Ticket, TicketApproval, TicketExecution.

FR-15: All ticket types.
FR-16: Lifecycle state management (open → in_process → closed).
FR-18: Mandatory notes on approval/rejection.
FR-20: Cancellation by handler.
SR-12: Dual approval enforcement.
SR-13: Execution traceability.
"""

from __future__ import annotations

import random
import string
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy.orm import Session

from backend.models.ticket import Ticket, TicketApproval, TicketExecution


def _generate_ticket_id() -> str:
    suffix = "".join(random.choices(string.digits, k=3))
    return f"T-{suffix}"


class TicketRepository:
    """Encapsulates all database operations for the Ticket workflow."""

    # --- Create ---

    def create(
        self,
        db: Session,
        *,
        case_id: str,
        ticket_type: str,
        description: str,
        created_by: uuid.UUID,
        linked_doc_ids: list[str] | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> Ticket:
        ticket_id = _generate_ticket_id()
        while db.query(Ticket).filter(Ticket.id == ticket_id).first():
            ticket_id = _generate_ticket_id()

        ticket = Ticket(
            id=ticket_id,
            case_id=case_id.strip().upper(),
            ticket_type=ticket_type,
            description=description,
            status="open",
            resolution="pending",
            linked_doc_ids=linked_doc_ids or [],
            parameters=parameters,
            created_by=created_by,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    # --- Read ---

    def get_by_id(self, db: Session, ticket_id: str) -> Ticket | None:
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def list_all(self, db: Session) -> Sequence[Ticket]:
        return db.query(Ticket).order_by(Ticket.created_at.desc()).all()

    def list_by_creator(self, db: Session, creator_id: uuid.UUID) -> Sequence[Ticket]:
        return (
            db.query(Ticket)
            .filter(Ticket.created_by == creator_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    # --- Approve / Reject ---

    def add_approval(
        self,
        db: Session,
        *,
        ticket: Ticket,
        stage: int,
        decision: str,
        decided_by: uuid.UUID,
        notes: str,
    ) -> TicketApproval:
        """Record an approval or rejection and advance ticket state."""
        approval = TicketApproval(
            id=uuid.uuid4(),
            ticket_id=ticket.id,
            stage=stage,
            decision=decision,
            decided_by=decided_by,
            notes=notes,
        )
        db.add(approval)

        now = datetime.now(timezone.utc)

        if decision == "rejected":
            ticket.status = "closed"
            ticket.resolution = "rejected"
            ticket.closed_at = now
        elif decision == "approved" and stage == 1:
            ticket.status = "in_process"
            ticket.resolution = "pending"
        elif decision == "approved" and stage == 2:
            ticket.status = "closed"
            ticket.resolution = "approved"
            ticket.closed_at = now

        db.commit()
        db.refresh(ticket)
        db.refresh(approval)
        return approval

    def get_approvals(self, db: Session, ticket_id: str) -> Sequence[TicketApproval]:
        return (
            db.query(TicketApproval)
            .filter(TicketApproval.ticket_id == ticket_id)
            .order_by(TicketApproval.decided_at.desc())
            .all()
        )

    # --- Assign ---

    def assign(self, db: Session, ticket: Ticket, assigned_to: uuid.UUID) -> Ticket:
        ticket.assigned_to = assigned_to
        db.commit()
        db.refresh(ticket)
        return ticket

    # --- Cancel (FR-20) ---

    def cancel(self, db: Session, ticket: Ticket) -> Ticket:
        """Cancel a ticket. Only allowed before final approval."""
        ticket.status = "closed"
        ticket.resolution = "cancelled"
        ticket.closed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)
        return ticket

    # --- Execute ---

    def record_execution(
        self,
        db: Session,
        *,
        ticket: Ticket,
        idempotency_key: str,
        executed_by: uuid.UUID,
        result: str,
        failure_reason: str | None = None,
    ) -> TicketExecution:
        execution = TicketExecution(
            id=uuid.uuid4(),
            ticket_id=ticket.id,
            idempotency_key=idempotency_key,
            executed_by=executed_by,
            result=result,
            failure_reason=failure_reason,
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def get_execution_by_idempotency_key(self, db: Session, key: str) -> TicketExecution | None:
        return db.query(TicketExecution).filter(TicketExecution.idempotency_key == key).first()

    def get_execution_by_ticket(self, db: Session, ticket_id: str) -> TicketExecution | None:
        return db.query(TicketExecution).filter(TicketExecution.ticket_id == ticket_id).first()


TICKET_REPO = TicketRepository()
