"""Ticket endpoints for SCFCA backend (PoC).

Role intent:
- regular: create tickets for assigned cases; view only own tickets
- administrator: view all; approve/reject; assign
- auditor: read-only view for traceability

Demo-safe only: in-memory store, no DB.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.auth.dependencies import Principal, require_any_role, get_current_principal
from backend.auth.schemas import Role

router = APIRouter()


TicketType = Literal["transfer_request", "custody_change", "release_request"]
TicketStatus = Literal["pending_review", "awaiting_second_approval", "approved", "rejected"]
TicketDecision = Literal["approved", "rejected"]


class TicketApprovalEvent(BaseModel):
    stage: Literal[1, 2]
    decision: TicketDecision
    decidedBy: str
    decidedAt: str


class TicketRecord(BaseModel):
    id: str
    caseId: str
    ticketType: TicketType
    description: str
    status: TicketStatus
    linkedDocumentIds: list[str] = []
    approvalHistory: list[TicketApprovalEvent] = []
    createdBy: str
    assignedTo: str | None = None


class TicketCreate(BaseModel):
    caseId: str
    ticketType: TicketType
    description: str
    linkedDocumentIds: list[str] = []


class TicketStatusUpdate(BaseModel):
    status: str


class TicketAssignUpdate(BaseModel):
    assignedTo: str


# In-memory demo tickets
TICKETS: list[TicketRecord] = [
    TicketRecord(
        id="T-201",
        caseId="C-100",
        ticketType="transfer_request",
        description="Transfer request awaiting admin approvals (PoC).",
        status="awaiting_second_approval",
        linkedDocumentIds=["DOC-77"],
        approvalHistory=[
            TicketApprovalEvent(stage=1, decision="approved", decidedBy="admin01", decidedAt="2026-03-19 12:10"),
        ],
        createdBy="ops_team",
        assignedTo="admin_team",
    ),
    TicketRecord(
        id="T-202",
        caseId="C-101",
        ticketType="custody_change",
        description="Custody change approved (PoC).",
        status="approved",
        linkedDocumentIds=["DOC-78"],
        approvalHistory=[
            TicketApprovalEvent(stage=1, decision="approved", decidedBy="admin01", decidedAt="2026-03-19 09:40"),
            TicketApprovalEvent(stage=2, decision="approved", decidedBy="admin02", decidedAt="2026-03-19 10:05"),
        ],
        createdBy="admin_team",
        assignedTo="admin_team",
    ),
]

# Demo case assignment mapping (must match demo case handlers)
CASE_ASSIGNMENTS: dict[str, str] = {
    "C-100": "ops_team",
    "C-101": "admin_team",
}


def _next_id(prefix: str) -> str:
    # Demo-only; not collision-safe.
    return f"{prefix}-{100 + len(TICKETS) + 1}"


def _is_assigned_case(principal: Principal, case_id: str) -> bool:
    assignee = CASE_ASSIGNMENTS.get(case_id)
    return assignee is not None and assignee == principal.username


@router.get("/", summary="List tickets", tags=["tickets"])
def list_tickets(principal: Principal = Depends(get_current_principal)):
    if principal.role == Role.regular:
        items = [t for t in TICKETS if t.createdBy == principal.username]
        return {"tickets": [t.model_dump() for t in items]}

    # admin + auditor can review system-wide
    return {"tickets": [t.model_dump() for t in TICKETS]}


@router.post("/", summary="Create ticket", tags=["tickets"])
def create_ticket(
    payload: TicketCreate,
    principal: Principal = Depends(require_any_role([Role.regular, Role.administrator])),
):
    case_id = (payload.caseId or "").strip().upper()
    ticket_type = payload.ticketType
    description = (payload.description or "").strip()

    if not case_id or not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="caseId and description are required")

    if principal.role == Role.regular and not _is_assigned_case(principal, case_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Case not assigned to user")

    record = TicketRecord(
        id=_next_id("T"),
        caseId=case_id,
        ticketType=ticket_type,
        description=description,
        status="pending_review",
        linkedDocumentIds=payload.linkedDocumentIds or [],
        approvalHistory=[],
        createdBy=principal.username,
        assignedTo=None,
    )
    TICKETS.insert(0, record)
    return {"ticket": record.model_dump()}


@router.patch("/{ticket_id}/status", summary="Update ticket status", tags=["tickets"])
def update_status(
    ticket_id: str,
    payload: TicketStatusUpdate,
    principal: Principal = Depends(require_any_role([Role.administrator])),
):
    next_status = (payload.status or "").strip().lower()
    if next_status == "pending":
        next_status = "pending_review"
    if next_status not in {"pending_review", "awaiting_second_approval", "approved", "rejected"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    for idx, t in enumerate(TICKETS):
        if t.id == ticket_id:
            updated = t.model_copy(update={"status": next_status})
            TICKETS[idx] = updated
            return {"ticket": updated.model_dump()}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")


@router.patch("/{ticket_id}/assign", summary="Assign ticket", tags=["tickets"])
def assign_ticket(
    ticket_id: str,
    payload: TicketAssignUpdate,
    principal: Principal = Depends(require_any_role([Role.administrator])),
):
    assignee = (payload.assignedTo or "").strip()
    if not assignee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="assignedTo is required")

    for idx, t in enumerate(TICKETS):
        if t.id == ticket_id:
            updated = t.model_copy(update={"assignedTo": assignee})
            TICKETS[idx] = updated
            return {"ticket": updated.model_dump()}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")


@router.post("/{ticket_id}/approve", summary="Approve ticket (2-step)", tags=["tickets"])
def approve_ticket(
    ticket_id: str,
    principal: Principal = Depends(require_any_role([Role.administrator])),
):
    for idx, t in enumerate(TICKETS):
        if t.id != ticket_id:
            continue

        if t.status in {"approved", "rejected"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is already finalized")

        approvals = [e for e in t.approvalHistory if e.decision == "approved"]
        if len(approvals) >= 2:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket already has two approvals")

        if any(e.decidedBy == principal.username and e.decision == "approved" for e in t.approvalHistory):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Administrator already approved")

        stage: Literal[1, 2] = 1 if len(approvals) == 0 else 2
        decided_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        event = TicketApprovalEvent(stage=stage, decision="approved", decidedBy=principal.username, decidedAt=decided_at)

        next_status: TicketStatus = "awaiting_second_approval" if stage == 1 else "approved"
        updated = t.model_copy(update={"status": next_status, "approvalHistory": [event, *t.approvalHistory]})
        TICKETS[idx] = updated
        return {"ticket": updated.model_dump()}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")


@router.post("/{ticket_id}/reject", summary="Reject ticket", tags=["tickets"])
def reject_ticket(
    ticket_id: str,
    principal: Principal = Depends(require_any_role([Role.administrator])),
):
    for idx, t in enumerate(TICKETS):
        if t.id != ticket_id:
            continue

        if t.status in {"approved", "rejected"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is already finalized")

        approvals = [e for e in t.approvalHistory if e.decision == "approved"]
        stage: Literal[1, 2] = 1 if len(approvals) == 0 else 2
        decided_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        event = TicketApprovalEvent(stage=stage, decision="rejected", decidedBy=principal.username, decidedAt=decided_at)

        updated = t.model_copy(update={"status": "rejected", "approvalHistory": [event, *t.approvalHistory]})
        TICKETS[idx] = updated
        return {"ticket": updated.model_dump()}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
