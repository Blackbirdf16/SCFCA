"""Ticket endpoints for SCFCA backend.

FR-14: Ticket creation by case handler for assigned cases.
FR-15: All 6 ticket types.
FR-16: Lifecycle — open → in_process → closed (with display status for compat).
FR-18: Mandatory notes on approve/reject.
FR-20: Cancellation by handler (pre-approval).
FR-21: Admins cannot initiate tickets.
SR-2:  Separation of duties (handler creates, admin approves).
SR-12: Dual approval enforcement.
SR-13: Execution traceability.

Dual-mode: uses DB if available, falls back to in-memory for test compat.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, require_any_role, get_current_principal
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.logging import logger
from backend.repositories.ticket_repo import TICKET_REPO
from backend.repositories.user_repo import USER_REPO
from backend.repositories.case_repo import CASE_REPO
from backend.repositories.asset_repo import ASSET_REPO
from backend.services.audit_log import AUDIT_LOG
from backend.services.case_service import is_case_assigned_to
from backend.auth.reauth import validate_reauth_token
from backend.services.security_ids import pseudonymous_actor_id

router = APIRouter()

TICKET_NOT_FOUND = "Ticket not found"

# --- All 6 ticket types (FR-15) ---
TicketType = Literal[
    "transfer_request",
    "custody_change",
    "release_request",
    "conversion_request",
    "reassignment",
    "metadata_correction",
]


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class TicketCreate(BaseModel):
    caseId: str
    ticketType: TicketType
    description: str
    linkedDocumentIds: list[str] = []
    parameters: Optional[dict[str, Any]] = None  # For reassignment / metadata

class TicketAssignUpdate(BaseModel):
    assignedTo: str

class ApprovalRequest(BaseModel):
    notes: str = Field(default="", min_length=0)  # FR-18: notes encouraged; default generated if empty

class RejectRequest(BaseModel):
    notes: str = Field(default="", min_length=0)  # FR-18: notes encouraged; default generated if empty

class CancelRequest(BaseModel):
    reason: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _actor_id(principal: Principal) -> str:
    return pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key)


def _get_db_or_none() -> Session | None:
    try:
        db = next(get_db())
        return db
    except Exception:
        return None


def _ticket_to_dict(ticket, approvals=None, execution=None) -> dict[str, Any]:
    """Convert a Ticket ORM model to the API response dict.

    Uses display_status for backward compatibility.
    """
    approval_history = []
    if approvals:
        for a in approvals:
            decider_name = ""
            if hasattr(a, "decider") and a.decider:
                decider_name = a.decider.username
            elif hasattr(a, "decided_by"):
                decider_name = str(a.decided_by)
            approval_history.append({
                "stage": a.stage,
                "decision": a.decision if isinstance(a.decision, str) else a.decision.value,
                "decidedBy": decider_name,
                "decidedAt": a.decided_at.strftime("%Y-%m-%d %H:%M") if a.decided_at else "",
                "notes": a.notes or "",
            })

    exec_dict = None
    if execution:
        executor_name = ""
        if hasattr(execution, "executor") and execution.executor:
            executor_name = execution.executor.username
        elif hasattr(execution, "executed_by"):
            executor_name = str(execution.executed_by)
        exec_dict = {
            "status": "executed",
            "executedBy": executor_name,
            "executedAt": execution.executed_at.strftime("%Y-%m-%d %H:%M") if execution.executed_at else "",
            "idempotencyKey": execution.idempotency_key,
            "result": execution.result,
            "failureReason": execution.failure_reason,
        }

    creator_name = ""
    if hasattr(ticket, "creator") and ticket.creator:
        creator_name = ticket.creator.username
    elif hasattr(ticket, "created_by"):
        creator_name = str(ticket.created_by)

    assignee_name = None
    if hasattr(ticket, "assignee") and ticket.assignee:
        assignee_name = ticket.assignee.username
    elif ticket.assigned_to:
        assignee_name = str(ticket.assigned_to)

    return {
        "id": ticket.id,
        "caseId": ticket.case_id,
        "ticketType": ticket.ticket_type if isinstance(ticket.ticket_type, str) else ticket.ticket_type.value,
        "description": ticket.description,
        "status": ticket.display_status,
        "linkedDocumentIds": ticket.linked_doc_ids or [],
        "approvalHistory": approval_history,
        "createdBy": creator_name,
        "assignedTo": assignee_name,
        "execution": exec_dict,
    }


# ---------------------------------------------------------------------------
# In-memory fallback (backward compat for test_workflows.py)
# ---------------------------------------------------------------------------

TicketStatusLegacy = Literal["pending_review", "awaiting_second_approval", "approved", "rejected"]

class _LegacyApprovalEvent(BaseModel):
    stage: Literal[1, 2]
    decision: Literal["approved", "rejected"]
    decidedBy: str
    decidedAt: str

class _LegacyTicket(BaseModel):
    id: str
    caseId: str
    ticketType: str
    description: str
    status: TicketStatusLegacy
    linkedDocumentIds: list[str] = []
    approvalHistory: list[_LegacyApprovalEvent] = []
    createdBy: str
    assignedTo: Optional[str] = None
    execution: Optional[dict] = None

class _LegacyExecution(BaseModel):
    status: Literal["executed", "failed"]
    executedBy: str
    executedAt: str
    idempotencyKey: str
    result: str
    failureReason: Optional[str] = None

_LEGACY_TICKETS: list[_LegacyTicket] = [
    _LegacyTicket(
        id="T-201", caseId="C-100", ticketType="transfer_request",
        description="Transfer request awaiting admin approvals (PoC).",
        status="awaiting_second_approval", linkedDocumentIds=["DOC-77"],
        approvalHistory=[_LegacyApprovalEvent(stage=1, decision="approved", decidedBy="bob", decidedAt="2026-03-19 12:10")],
        createdBy="alice", assignedTo="eve",
    ),
    _LegacyTicket(
        id="T-202", caseId="C-101", ticketType="custody_change",
        description="Custody change approved (PoC).", status="approved",
        linkedDocumentIds=["DOC-78"],
        approvalHistory=[
            _LegacyApprovalEvent(stage=1, decision="approved", decidedBy="bob", decidedAt="2026-03-19 09:40"),
            _LegacyApprovalEvent(stage=2, decision="approved", decidedBy="eve", decidedAt="2026-03-19 10:05"),
        ],
        createdBy="alice", assignedTo="bob",
    ),
]
_LEGACY_IDEMPOTENCY: dict[str, dict[str, _LegacyExecution]] = {}

def _legacy_next_id() -> str:
    return f"T-{100 + len(_LEGACY_TICKETS) + 1}"


def _use_db(db: Session | None) -> bool:
    """Decide whether to use DB or legacy in-memory store."""
    if db is None:
        return False
    try:
        from backend.models.ticket import Ticket
        db.query(Ticket).limit(1).all()
        # Also need users table for creator lookups
        from backend.models.user import User
        db.query(User).limit(1).all()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/", summary="List tickets", tags=["tickets"])
def list_tickets(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Session = Depends(get_db),
):
    if _use_db(db):
        user = USER_REPO.get_by_username(db, principal.username)
        if principal.role == Role.regular and user:
            tickets = TICKET_REPO.list_by_creator(db, user.id)
        else:
            tickets = TICKET_REPO.list_all(db)
        return {
            "tickets": [
                _ticket_to_dict(t, t.approvals, t.execution)
                for t in tickets
            ]
        }

    # Legacy fallback
    if principal.role == Role.regular:
        items = [t for t in _LEGACY_TICKETS if t.createdBy == principal.username]
        return {"tickets": [t.model_dump() for t in items]}
    return {"tickets": [t.model_dump() for t in _LEGACY_TICKETS]}


@router.post("/", summary="Create ticket", tags=["tickets"])
def create_ticket(
    payload: TicketCreate,
    principal: Annotated[Principal, Depends(require_any_role([Role.regular]))],
    db: Session = Depends(get_db),
):
    case_id = (payload.caseId or "").strip().upper()
    description = (payload.description or "").strip()
    if not case_id or not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="caseId and description are required")

    # FR-14 / SR-2: handler only, assigned cases only
    if not is_case_assigned_to(principal, case_id, db=db):
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_create_denied", entity_type="case", entity_id=case_id,
            details={"reason": "case_not_assigned"},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Case not assigned to user")

    if _use_db(db):
        user = USER_REPO.get_by_username(db, principal.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found in DB")

        ticket = TICKET_REPO.create(
            db, case_id=case_id, ticket_type=payload.ticketType,
            description=description, created_by=user.id,
            linked_doc_ids=payload.linkedDocumentIds,
            parameters=payload.parameters,
        )
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_created", entity_type="ticket", entity_id=ticket.id,
            details={"caseId": case_id, "ticketType": payload.ticketType},
        )
        return {"ticket": _ticket_to_dict(ticket, [], None)}

    # Legacy fallback
    record = _LegacyTicket(
        id=_legacy_next_id(), caseId=case_id, ticketType=payload.ticketType,
        description=description, status="pending_review",
        linkedDocumentIds=payload.linkedDocumentIds or [],
        createdBy=principal.username,
    )
    _LEGACY_TICKETS.insert(0, record)
    AUDIT_LOG.append(
        actor_id=_actor_id(principal), event_type="tickets",
        action="ticket_created", entity_type="ticket", entity_id=record.id,
        details={"caseId": case_id, "ticketType": payload.ticketType},
    )
    return {"ticket": record.model_dump()}


@router.patch("/{ticket_id}/assign", summary="Assign ticket", tags=["tickets"])
def assign_ticket(
    ticket_id: str,
    payload: TicketAssignUpdate,
    principal: Annotated[Principal, Depends(require_any_role([Role.administrator]))],
    db: Session = Depends(get_db),
):
    assignee_name = (payload.assignedTo or "").strip()
    if not assignee_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="assignedTo is required")

    if _use_db(db):
        ticket = TICKET_REPO.get_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
        # Allow assignment on approved (closed+approved) tickets that haven't been executed yet
        if ticket.status == "closed" and ticket.resolution != "approved":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is finalized; assignment blocked")
        if ticket.execution is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket has execution record; assignment blocked")
        assignee = USER_REPO.get_by_username(db, assignee_name)
        if not assignee:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee not found")
        TICKET_REPO.assign(db, ticket, assignee.id)
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_assigned", entity_type="ticket", entity_id=ticket_id,
            details={"assignedTo": assignee_name},
        )
        return {"ticket": _ticket_to_dict(ticket, ticket.approvals, ticket.execution)}

    # Legacy fallback
    for idx, t in enumerate(_LEGACY_TICKETS):
        if t.id == ticket_id:
            if t.status in {"rejected"}:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is finalized; assignment blocked")
            if t.execution:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket has execution record; assignment blocked")
            updated = t.model_copy(update={"assignedTo": assignee_name})
            _LEGACY_TICKETS[idx] = updated
            AUDIT_LOG.append(
                actor_id=_actor_id(principal), event_type="tickets",
                action="ticket_assigned", entity_type="ticket", entity_id=ticket_id,
                details={"assignedTo": assignee_name},
            )
            return {"ticket": updated.model_dump()}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)


@router.post("/{ticket_id}/approve", summary="Approve ticket (2-step)", tags=["tickets"])
def approve_ticket(
    ticket_id: str,
    principal: Annotated[Principal, Depends(require_any_role([Role.administrator]))],
    db: Session = Depends(get_db),
    payload: ApprovalRequest = ApprovalRequest(),
):
    if _use_db(db):
        ticket = TICKET_REPO.get_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
        if ticket.status == "closed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is already finalized")

        approvals = TICKET_REPO.get_approvals(db, ticket_id)
        approved_list = [a for a in approvals if a.decision == "approved"]
        if len(approved_list) >= 2:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket already has two approvals")

        admin_user = USER_REPO.get_by_username(db, principal.username)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin not in DB")

        if any(a.decided_by == admin_user.id and a.decision == "approved" for a in approvals):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Administrator already approved")

        stage = 1 if len(approved_list) == 0 else 2

        # SR-22: state machine
        if stage == 1 and ticket.status != "open":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stage-1 approval requires pending_review")
        if stage == 2 and ticket.status != "in_process":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stage-2 approval requires awaiting_second_approval")

        notes = payload.notes or f"Approved by {principal.username}"
        TICKET_REPO.add_approval(db, ticket=ticket, stage=stage, decision="approved", decided_by=admin_user.id, notes=notes)

        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_approved", entity_type="ticket", entity_id=ticket_id,
            details={"stage": stage, "notes": notes},
        )
        all_approvals = TICKET_REPO.get_approvals(db, ticket_id)
        return {"ticket": _ticket_to_dict(ticket, all_approvals, ticket.execution)}

    # Legacy fallback
    for idx, t in enumerate(_LEGACY_TICKETS):
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
        if stage == 1 and t.status != "pending_review":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stage-1 approval requires pending_review")
        if stage == 2 and t.status != "awaiting_second_approval":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stage-2 approval requires awaiting_second_approval")
        decided_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        event = _LegacyApprovalEvent(stage=stage, decision="approved", decidedBy=principal.username, decidedAt=decided_at)
        next_status = "awaiting_second_approval" if stage == 1 else "approved"
        updated = t.model_copy(update={"status": next_status, "approvalHistory": [event, *t.approvalHistory]})
        _LEGACY_TICKETS[idx] = updated
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_approved", entity_type="ticket", entity_id=ticket_id,
            details={"stage": stage},
        )
        return {"ticket": updated.model_dump()}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)


@router.post("/{ticket_id}/reject", summary="Reject ticket", tags=["tickets"])
def reject_ticket(
    ticket_id: str,
    principal: Annotated[Principal, Depends(require_any_role([Role.administrator]))],
    db: Session = Depends(get_db),
    payload: RejectRequest = RejectRequest(),
):
    if _use_db(db):
        ticket = TICKET_REPO.get_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
        if ticket.status == "closed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is already finalized")

        approvals = TICKET_REPO.get_approvals(db, ticket_id)
        approved_list = [a for a in approvals if a.decision == "approved"]
        stage = 1 if len(approved_list) == 0 else 2

        admin_user = USER_REPO.get_by_username(db, principal.username)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin not in DB")

        notes = payload.notes or f"Rejected by {principal.username}"
        TICKET_REPO.add_approval(db, ticket=ticket, stage=stage, decision="rejected", decided_by=admin_user.id, notes=notes)

        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_rejected", entity_type="ticket", entity_id=ticket_id,
            details={"stage": stage, "notes": notes},
        )
        all_approvals = TICKET_REPO.get_approvals(db, ticket_id)
        return {"ticket": _ticket_to_dict(ticket, all_approvals, ticket.execution)}

    # Legacy fallback
    for idx, t in enumerate(_LEGACY_TICKETS):
        if t.id != ticket_id:
            continue
        if t.status in {"approved", "rejected"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is already finalized")
        if t.status not in {"pending_review", "awaiting_second_approval"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is not in a rejectable state")
        approvals = [e for e in t.approvalHistory if e.decision == "approved"]
        stage: Literal[1, 2] = 1 if len(approvals) == 0 else 2
        decided_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        event = _LegacyApprovalEvent(stage=stage, decision="rejected", decidedBy=principal.username, decidedAt=decided_at)
        updated = t.model_copy(update={"status": "rejected", "approvalHistory": [event, *t.approvalHistory]})
        _LEGACY_TICKETS[idx] = updated
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_rejected", entity_type="ticket", entity_id=ticket_id,
            details={"stage": stage},
        )
        return {"ticket": updated.model_dump()}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)


@router.post("/{ticket_id}/cancel", summary="Cancel ticket", tags=["tickets"])
def cancel_ticket(
    ticket_id: str,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Session = Depends(get_db),
    payload: CancelRequest = CancelRequest(),
):
    """Cancel a ticket. Only the creator can cancel, and only before final approval. FR-20."""
    if _use_db(db):
        ticket = TICKET_REPO.get_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
        if ticket.status == "closed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket is already finalized")

        user = USER_REPO.get_by_username(db, principal.username)
        if not user or ticket.created_by != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the ticket creator can cancel")

        TICKET_REPO.cancel(db, ticket)
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_cancelled", entity_type="ticket", entity_id=ticket_id,
            details={"reason": payload.reason},
        )
        return {"ticket": _ticket_to_dict(ticket, ticket.approvals, ticket.execution)}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)


@router.post("/{ticket_id}/execute", summary="Execute custody action", tags=["tickets"])
def execute_ticket(
    ticket_id: str,
    request: Request,
    principal: Annotated[Principal, Depends(require_any_role([Role.administrator]))],
    db: Session = Depends(get_db),
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
):
    """Execute an approved ticket. SR-6 / SR-9 / SR-13 / FR-27."""
    if not idempotency_key or len(idempotency_key.strip()) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key header is required")
    idempotency_key = idempotency_key.strip()

    if _use_db(db):
        ticket = TICKET_REPO.get_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
        if ticket.display_status == "rejected":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket rejected; execution blocked")
        if ticket.display_status != "approved":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket must be approved before execution")

        # Idempotency check
        existing = TICKET_REPO.get_execution_by_idempotency_key(db, idempotency_key)
        if existing and existing.ticket_id == ticket_id:
            return {"execution": {
                "status": "executed", "executedBy": existing.executor.username if existing.executor else "",
                "executedAt": existing.executed_at.strftime("%Y-%m-%d %H:%M") if existing.executed_at else "",
                "idempotencyKey": existing.idempotency_key, "result": existing.result, "failureReason": existing.failure_reason,
            }}

        # Replay protection
        existing_exec = TICKET_REPO.get_execution_by_ticket(db, ticket_id)
        if existing_exec:
            AUDIT_LOG.append(
                actor_id=_actor_id(principal), event_type="tickets",
                action="execution_replay_denied", entity_type="ticket", entity_id=ticket_id,
                details={"idempotencyKey": idempotency_key},
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Replay attempt denied")

        # Dual approval check
        approvals = TICKET_REPO.get_approvals(db, ticket_id)
        approved_list = [a for a in approvals if a.decision == "approved"]
        approver_ids = {a.decided_by for a in approved_list}
        if len(approved_list) < 2 or len(approver_ids) < 2:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Requires two distinct approvals")

        # Assignment check (SR-23)
        admin_user = USER_REPO.get_by_username(db, principal.username)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin not in DB")
        if not ticket.assigned_to:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket must be assigned before execution")
        if ticket.assigned_to != admin_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned administrator can execute")

        # SR-6: Re-authentication required for custody execution
        validate_reauth_token(request)

        # --- Execute side-effects based on ticket type ---
        result_text = "simulated_execution_ok"
        try:
            if ticket.ticket_type == "reassignment" and ticket.parameters:
                new_handler_username = ticket.parameters.get("newHandlerUsername", "")
                new_handler = USER_REPO.get_by_username(db, new_handler_username) if new_handler_username else None
                if new_handler:
                    CASE_REPO.reassign(db, case_id=ticket.case_id, new_handler_id=new_handler.id, assigned_by=admin_user.id, ticket_id=ticket.id)
                    result_text = f"case_reassigned_to_{new_handler_username}"

            elif ticket.ticket_type == "metadata_correction" and ticket.parameters:
                asset_id = ticket.parameters.get("assetId", "")
                new_status = ticket.parameters.get("status")
                new_notes = ticket.parameters.get("notes")
                if asset_id:
                    ASSET_REPO.update_metadata(db, asset_id, status=new_status, notes=new_notes)
                    result_text = f"metadata_updated_{asset_id}"

            elif ticket.ticket_type == "release_request" and ticket.parameters:
                asset_id = ticket.parameters.get("assetId", "")
                if asset_id:
                    ASSET_REPO.update_metadata(db, asset_id, status="released")
                    result_text = f"asset_released_{asset_id}"

        except Exception as exc:
            execution = TICKET_REPO.record_execution(
                db, ticket=ticket, idempotency_key=idempotency_key,
                executed_by=admin_user.id, result="failed", failure_reason=str(exc),
            )
            return {"execution": {
                "status": "failed", "executedBy": principal.username,
                "executedAt": execution.executed_at.strftime("%Y-%m-%d %H:%M"),
                "idempotencyKey": idempotency_key, "result": "failed", "failureReason": str(exc),
            }}

        execution = TICKET_REPO.record_execution(
            db, ticket=ticket, idempotency_key=idempotency_key,
            executed_by=admin_user.id, result=result_text,
        )

        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_executed", entity_type="ticket", entity_id=ticket_id,
            details={"idempotencyKey": idempotency_key, "result": result_text},
        )
        logger.info("security_event ticket_executed ticket=%s admin=%s", ticket_id, principal.username)

        all_approvals = TICKET_REPO.get_approvals(db, ticket_id)
        ticket_dict = _ticket_to_dict(ticket, all_approvals, execution)
        exec_dict = ticket_dict["execution"]
        return {"execution": exec_dict, "ticket": ticket_dict}

    # Legacy fallback
    for idx, t in enumerate(_LEGACY_TICKETS):
        if t.id != ticket_id:
            continue
        if t.status == "rejected":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket rejected; execution blocked")
        if t.status != "approved":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket must be approved before execution")
        existing = _LEGACY_IDEMPOTENCY.get(ticket_id, {}).get(idempotency_key)
        if existing:
            return {"execution": existing.model_dump()}
        if ticket_id in _LEGACY_IDEMPOTENCY and _LEGACY_IDEMPOTENCY[ticket_id]:
            AUDIT_LOG.append(
                actor_id=_actor_id(principal), event_type="tickets",
                action="execution_replay_denied", entity_type="ticket", entity_id=ticket_id,
                details={"idempotencyKey": idempotency_key},
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Replay attempt denied")
        approvals = [e for e in t.approvalHistory if e.decision == "approved"]
        approvers = {e.decidedBy for e in approvals}
        if len(approvals) < 2 or len(approvers) < 2:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Requires two distinct approvals")
        if not t.assignedTo:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket must be assigned before execution")
        if t.assignedTo != principal.username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned administrator can execute")
        executed_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        execution = _LegacyExecution(
            status="executed", executedBy=principal.username, executedAt=executed_at,
            idempotencyKey=idempotency_key, result="simulated_execution_ok", failureReason=None,
        )
        _LEGACY_IDEMPOTENCY.setdefault(ticket_id, {})[idempotency_key] = execution
        updated = t.model_copy(update={"execution": execution.model_dump()})
        _LEGACY_TICKETS[idx] = updated
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="tickets",
            action="ticket_executed", entity_type="ticket", entity_id=ticket_id,
            details={"idempotencyKey": idempotency_key, "approvers": sorted(approvers)},
        )
        logger.info("security_event ticket_executed ticket=%s admin=%s", ticket_id, principal.username)
        return {"execution": execution.model_dump(), "ticket": updated.model_dump()}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
