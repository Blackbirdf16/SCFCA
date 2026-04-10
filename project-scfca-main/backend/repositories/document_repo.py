"""Document repository — data access for DocumentRecord model.

FR-22: PDF-only documentation.
FR-23: Document integrity hashing.
SR-16: Document integrity verification.
NFR-4: Persistent storage.
"""

from __future__ import annotations

import random
import string
import uuid
from hashlib import sha256
from typing import Sequence

from sqlalchemy.orm import Session

from backend.models.document import DocumentRecord


def _generate_doc_id() -> str:
    suffix = "".join(random.choices(string.digits, k=3))
    return f"DOC-{suffix}"


class DocumentRepository:
    """Encapsulates DB operations for document metadata."""

    def create(
        self,
        db: Session,
        *,
        filename: str,
        content_type: str,
        content: bytes,
        uploaded_by: uuid.UUID,
        case_id: str | None = None,
        ticket_id: str | None = None,
    ) -> tuple[DocumentRecord, str]:
        """Create document metadata. Returns (record, sha256_hex)."""
        digest = sha256(content).hexdigest()
        size = len(content)

        doc_id = _generate_doc_id()
        while db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first():
            doc_id = _generate_doc_id()

        record = DocumentRecord(
            id=doc_id,
            filename=filename,
            content_type=content_type,
            sha256_hex=digest,
            size_bytes=size,
            case_id=case_id,
            ticket_id=ticket_id,
            uploaded_by=uploaded_by,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record, digest

    def get_by_id(self, db: Session, doc_id: str) -> DocumentRecord | None:
        return db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()

    def list_all(self, db: Session) -> Sequence[DocumentRecord]:
        return db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()

    def list_by_uploader(self, db: Session, uploader_id: uuid.UUID) -> Sequence[DocumentRecord]:
        return (
            db.query(DocumentRecord)
            .filter(DocumentRecord.uploaded_by == uploader_id)
            .order_by(DocumentRecord.created_at.desc())
            .all()
        )

    def list_by_case(self, db: Session, case_id: str) -> Sequence[DocumentRecord]:
        return (
            db.query(DocumentRecord)
            .filter(DocumentRecord.case_id == case_id)
            .order_by(DocumentRecord.created_at.desc())
            .all()
        )


DOCUMENT_REPO = DocumentRepository()
