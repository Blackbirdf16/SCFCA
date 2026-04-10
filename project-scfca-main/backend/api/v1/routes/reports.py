"""Report generation endpoints for SCFCA.

FR-24: Audit report — system-wide activity PDF for admin/auditor.
FR-25: Case report — per-case PDF with assets, tickets, documents.
FR-26: Reports are informational snapshots (no state mutation).
NFR-10: Structured reports suitable for institutional/judicial use.
"""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, require_any_role
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.repositories.case_repo import CASE_REPO
from backend.repositories.asset_repo import ASSET_REPO
from backend.repositories.document_repo import DOCUMENT_REPO
from backend.repositories.ticket_repo import TICKET_REPO
from backend.repositories.user_repo import USER_REPO
from backend.services.audit_log import AUDIT_LOG
from backend.services.report_generator import generate_audit_report, generate_case_report
from backend.services.security_ids import pseudonymous_actor_id

router = APIRouter()


@router.get("/audit", summary="Download audit report PDF", tags=["reports"])
def audit_report(
    principal: Annotated[Principal, Depends(require_any_role([Role.administrator, Role.auditor]))],
    from_date: Optional[str] = Query(None, description="Filter from date (ISO)"),
    to_date: Optional[str] = Query(None, description="Filter to date (ISO)"),
):
    """Generate and download a system-wide audit report. FR-24."""
    events = AUDIT_LOG.list(limit=2000)
    chain_status = AUDIT_LOG.verify_chain()

    pdf_bytes = generate_audit_report(events, chain_status, from_date, to_date)

    # Log the download (FR-26: reports don't modify state, but the download is tracked)
    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="reports",
        action="audit_report_downloaded",
        entity_type="report",
        entity_id="audit",
        details={"from_date": from_date, "to_date": to_date, "event_count": len(events)},
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="scfca_audit_report.pdf"'},
    )


@router.get("/case/{case_id}", summary="Download case report PDF", tags=["reports"])
def case_report(
    case_id: str,
    principal: Annotated[Principal, Depends(require_any_role([Role.administrator, Role.regular]))],
    db: Session = Depends(get_db),
):
    """Generate and download a per-case report. FR-25."""
    case = CASE_REPO.get_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Regular users can only download reports for assigned cases
    handler_name = case.handler.username if case.handler else "unknown"
    if principal.role == Role.regular and handler_name != principal.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this case")

    assets = ASSET_REPO.list_by_case(db, case_id)

    # Get tickets for this case
    all_tickets = TICKET_REPO.list_all(db)
    case_tickets = [t for t in all_tickets if t.case_id == case_id.strip().upper()]

    documents = DOCUMENT_REPO.list_by_case(db, case_id)

    pdf_bytes = generate_case_report(case, assets, case_tickets, documents, handler_name)

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="reports",
        action="case_report_downloaded",
        entity_type="case",
        entity_id=case_id,
        details={"asset_count": len(assets), "ticket_count": len(case_tickets), "doc_count": len(documents)},
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="scfca_case_{case_id}.pdf"'},
    )
