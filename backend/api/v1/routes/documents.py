"""Document endpoints for SCFCA backend (PoC).

Role intent:
- regular: upload documents for assigned cases; view only own uploads
- administrator: view all; can upload
- auditor: read-only access for evidence/traceability

Demo-safe only: in-memory store, no file handling.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.auth.dependencies import Principal, get_current_principal, require_any_role
from backend.auth.schemas import Role

router = APIRouter()


class DocumentRecord(BaseModel):
    id: str
    name: str
    hash: str
    createdAt: str
    caseId: str | None = None
    walletRef: str | None = None
    uploadedBy: str


class DocumentCreate(BaseModel):
    name: str
    hash: str
    createdAt: str
    caseId: str | None = None
    walletRef: str | None = None


DOCUMENTS: list[DocumentRecord] = [
    DocumentRecord(
        id="DOC-77",
        name="custody_policy_v2.pdf",
        hash="sha256:AA1BB2CC3",
        createdAt="2026-03-18",
        caseId="C-100",
        walletRef="WLT-8F3A-PRIMARY",
        uploadedBy="ops_team",
    ),
    DocumentRecord(
        id="DOC-78",
        name="audit_trace_Q1.csv",
        hash="sha256:DD4EE5FF6",
        createdAt="2026-03-19",
        caseId="C-101",
        walletRef="WLT-21C9-MSIG",
        uploadedBy="admin_team",
    ),
]

# Demo case assignment mapping (must match demo case handlers)
CASE_ASSIGNMENTS: dict[str, str] = {
    "C-100": "ops_team",
    "C-101": "admin_team",
}


def _next_id(prefix: str) -> str:
    return f"{prefix}-{100 + len(DOCUMENTS) + 1}"


def _is_assigned_case(principal: Principal, case_id: str) -> bool:
    assignee = CASE_ASSIGNMENTS.get(case_id)
    return assignee is not None and assignee == principal.username


@router.get("/", summary="List documents", tags=["documents"])
def list_documents(principal: Principal = Depends(get_current_principal)):
    if principal.role == Role.regular:
        items = [d for d in DOCUMENTS if d.uploadedBy == principal.username]
        return {"documents": [d.model_dump() for d in items]}

    return {"documents": [d.model_dump() for d in DOCUMENTS]}


@router.post("/", summary="Upload/register document", tags=["documents"])
def upload_document(
    payload: DocumentCreate,
    principal: Principal = Depends(require_any_role([Role.regular, Role.administrator])),
):
    name = (payload.name or "").strip()
    doc_hash = (payload.hash or "").strip()
    created_at = (payload.createdAt or "").strip()

    if not name or not doc_hash or not created_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name, hash, createdAt are required")

    case_id = payload.caseId.strip().upper() if payload.caseId else None
    wallet_ref = payload.walletRef.strip().upper() if payload.walletRef else None

    if principal.role == Role.regular:
        if not case_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="caseId is required for regular users")
        if not _is_assigned_case(principal, case_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Case not assigned to user")

    record = DocumentRecord(
        id=_next_id("DOC"),
        name=name,
        hash=doc_hash,
        createdAt=created_at,
        caseId=case_id,
        walletRef=wallet_ref,
        uploadedBy=principal.username,
    )

    DOCUMENTS.insert(0, record)
    return {"document": record.model_dump()}
