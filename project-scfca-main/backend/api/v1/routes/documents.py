"""Document endpoints for SCFCA backend.

FR-22: PDF-only upload with magic byte + MIME + extension validation.
FR-23: Server-side SHA-256 hashing on upload, integrity verification.
SR-16: Document integrity verification via recomputed hash.
NFR-4: Persistent storage (DB metadata + filesystem bytes).

Dual-mode: DB + filesystem when available, in-memory fallback for tests.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, get_current_principal, require_any_role
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.repositories.document_repo import DOCUMENT_REPO
from backend.repositories.user_repo import USER_REPO
from backend.services.audit_log import AUDIT_LOG
from backend.services.case_service import get_case, is_case_assigned_to
from backend.services.document_service import DOCUMENT_STORE
from backend.services.file_storage import FILE_STORAGE
from backend.services.security_ids import pseudonymous_actor_id

router = APIRouter()


def _actor_id(principal: Principal) -> str:
    return pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key)


def _is_pdf(upload: UploadFile, content: bytes) -> bool:
    content_type_ok = (upload.content_type or "").lower() == "application/pdf"
    name_ok = (upload.filename or "").lower().endswith(".pdf")
    magic_ok = content.startswith(b"%PDF-")
    return bool(content_type_ok and name_ok and magic_ok)


def _use_db(db: Session | None) -> bool:
    if db is None:
        return False
    try:
        from backend.models.document import DocumentRecord
        from backend.models.user import User
        db.query(DocumentRecord).limit(1).all()
        db.query(User).limit(1).all()
        return True
    except Exception:
        return False


def _doc_to_dict(doc, wallet_ref: str | None = None) -> dict:
    created_at = doc.created_at
    if hasattr(created_at, "isoformat"):
        created_at = created_at.date().isoformat() if hasattr(created_at, "date") else str(created_at)

    uploader_name = ""
    if hasattr(doc, "uploaded_by"):
        uploader_name = str(doc.uploaded_by)

    return {
        "id": doc.id,
        "name": doc.filename,
        "hash": f"sha256:{doc.sha256_hex}",
        "createdAt": created_at,
        "caseId": doc.case_id,
        "walletRef": wallet_ref,
        "uploadedBy": uploader_name,
        "ticketId": doc.ticket_id,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/", summary="List documents", tags=["documents"])
def list_documents(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Session = Depends(get_db),
):
    if _use_db(db):
        user = USER_REPO.get_by_username(db, principal.username)
        if principal.role == Role.regular and user:
            docs = DOCUMENT_REPO.list_by_uploader(db, user.id)
        else:
            docs = DOCUMENT_REPO.list_all(db)
        return {
            "documents": [_doc_to_dict(d) for d in docs]
        }

    # Legacy in-memory fallback
    if principal.role == Role.regular:
        docs = [d for d in DOCUMENT_STORE.list() if d.uploader == principal.username]
    else:
        docs = DOCUMENT_STORE.list()

    return {
        "documents": [
            {
                "id": d.id,
                "name": d.filename,
                "hash": f"sha256:{d.sha256_hex}",
                "createdAt": d.created_at,
                "caseId": d.case_id,
                "walletRef": (get_case(d.case_id).wallet_ref if d.case_id and get_case(d.case_id) else None),
                "uploadedBy": d.uploader,
                "ticketId": d.ticket_id,
            }
            for d in docs
        ]
    }


@router.post("/", summary="Upload document (PDF-only)", tags=["documents"])
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    principal: Annotated[Principal, Depends(require_any_role([Role.regular, Role.administrator]))],
    db: Session = Depends(get_db),
    case_id: Annotated[Optional[str], Form(alias="caseId")] = None,
    ticket_id: Annotated[Optional[str], Form(alias="ticketId")] = None,
):
    case_id = case_id.strip().upper() if case_id else None
    ticket_id = ticket_id.strip().upper() if ticket_id else None

    if principal.role == Role.regular:
        if not case_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="caseId is required for regular users")
        if not is_case_assigned_to(principal, case_id, db=db):
            AUDIT_LOG.append(
                actor_id=_actor_id(principal), event_type="documents",
                action="document_upload_denied", entity_type="case", entity_id=case_id,
                details={"reason": "case_not_assigned"},
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Case not assigned to user")

    content = await file.read()
    if not _is_pdf(file, content):
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="documents",
            action="document_upload_denied", entity_type="document", entity_id=None,
            details={"reason": "pdf_only"},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    if _use_db(db):
        user = USER_REPO.get_by_username(db, principal.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found in DB")

        record, digest = DOCUMENT_REPO.create(
            db,
            filename=(file.filename or "document.pdf"),
            content_type=(file.content_type or "application/pdf"),
            content=content,
            uploaded_by=user.id,
            case_id=case_id,
            ticket_id=ticket_id,
        )
        FILE_STORAGE.save(record.id, content)

        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="documents",
            action="document_uploaded", entity_type="document", entity_id=record.id,
            details={"caseId": case_id, "ticketId": ticket_id, "sha256": digest, "filename": record.filename},
        )
        return {"document": _doc_to_dict(record)}

    # Legacy in-memory fallback
    created = DOCUMENT_STORE.create(
        filename=(file.filename or "document.pdf"),
        content_type=(file.content_type or "application/pdf"),
        content=content, uploader=principal.username,
        case_id=case_id, ticket_id=ticket_id,
    )
    AUDIT_LOG.append(
        actor_id=_actor_id(principal), event_type="documents",
        action="document_uploaded", entity_type="document", entity_id=created.id,
        details={"caseId": case_id, "ticketId": ticket_id, "sha256": created.sha256_hex, "filename": created.filename},
    )
    case = get_case(case_id) if case_id else None
    return {
        "document": {
            "id": created.id, "name": created.filename,
            "hash": f"sha256:{created.sha256_hex}", "createdAt": created.created_at,
            "caseId": case_id, "walletRef": (case.wallet_ref if case else None),
            "uploadedBy": principal.username, "ticketId": ticket_id,
        }
    }


@router.get("/{document_id}/verify", summary="Verify document integrity", tags=["documents"])
def verify_document(
    document_id: str,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Session = Depends(get_db),
):
    if _use_db(db):
        record = DOCUMENT_REPO.get_by_id(db, document_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        content = FILE_STORAGE.load(record.id)
        if content is None:
            return {"ok": False, "reason": "file_not_found", "documentId": record.id}

        recomputed = sha256(content).hexdigest()
        ok = recomputed == record.sha256_hex
        report = {"ok": ok, "documentId": record.id, "expected": record.sha256_hex, "actual": recomputed}

        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="documents",
            action="document_verified", entity_type="document", entity_id=record.id,
            details={"ok": ok, "expected": record.sha256_hex, "actual": recomputed},
        )
        if not ok:
            AUDIT_LOG.append(
                actor_id=_actor_id(principal), event_type="security",
                action="document_integrity_mismatch", entity_type="document", entity_id=record.id,
                details={"expected": record.sha256_hex, "actual": recomputed},
            )
        return report

    # Legacy in-memory fallback
    doc = DOCUMENT_STORE.get(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if principal.role == Role.regular and doc.uploader != principal.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    report = DOCUMENT_STORE.verify(doc.id)
    AUDIT_LOG.append(
        actor_id=_actor_id(principal), event_type="documents",
        action="document_verified", entity_type="document", entity_id=doc.id,
        details={"ok": report.get("ok"), "expected": report.get("expected"), "actual": report.get("actual")},
    )
    if report.get("ok") is False:
        AUDIT_LOG.append(
            actor_id=_actor_id(principal), event_type="security",
            action="document_integrity_mismatch", entity_type="document", entity_id=doc.id,
            details={"expected": report.get("expected"), "actual": report.get("actual")},
        )
    return report


@router.get("/{document_id}/download", summary="Download document", tags=["documents"])
def download_document(
    document_id: str,
    principal: Annotated[Principal, Depends(require_any_role([Role.regular, Role.administrator, Role.auditor]))],
    db: Session = Depends(get_db),
):
    """Download the original PDF file. FR-23."""
    if _use_db(db):
        record = DOCUMENT_REPO.get_by_id(db, document_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        content = FILE_STORAGE.load(record.id)
        if content is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage")

        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{record.filename}"'},
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
