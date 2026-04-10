"""Document ORM model for SCFCA.

FR-22: PDF-only documentation.
FR-23: Document integrity hashing — SHA-256 stored on upload.
SR-16: Document integrity verification.
NFR-4: Long-term data retention via DB persistence.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from backend.core.database import Base
from backend.models.user import UUIDType


class DocumentRecord(Base):
    """A PDF document uploaded as evidence for a case or ticket.

    Metadata stored in DB; raw bytes stored on filesystem at
    data/documents/{id}.pdf — swappable for S3 in production.
    """

    __tablename__ = "documents"

    id = Column(String(8), primary_key=True)  # DOC-XXXX
    filename = Column(String(256), nullable=False)
    content_type = Column(String(64), nullable=False)
    sha256_hex = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    case_id = Column(String(8), ForeignKey("cases.id"), nullable=True, index=True)
    ticket_id = Column(String(8), ForeignKey("tickets.id"), nullable=True, index=True)
    uploaded_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
