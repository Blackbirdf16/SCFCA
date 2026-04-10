"""Case ORM models for SCFCA.

FR-5:  Case creation with unique, random, non-semantic CaseID.
FR-6:  Case assignment — exactly one handler at a time.
FR-9:  Immutable assignment history with timestamps and ticket references.
SR-17: CaseIDs are never deleted.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.models.user import UUIDType


class Case(Base):
    """A custody case linked to seized cryptocurrency assets.

    The id (CaseID) is non-semantic and never deleted (SR-17).
    """

    __tablename__ = "cases"

    id = Column(String(8), primary_key=True)  # C-XXXX
    title = Column(String(256), nullable=False)
    wallet_ref = Column(String(64), nullable=False)
    handler_id = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    custody_status = Column(
        Enum("open", "in_review", "closed", name="custody_status_enum", native_enum=False),
        nullable=False,
        default="open",
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)

    # Relationships
    handler = relationship("User", foreign_keys=[handler_id])
    assignments = relationship("CaseAssignmentHistory", back_populates="case", order_by="CaseAssignmentHistory.assigned_at.desc()")


class CaseAssignmentHistory(Base):
    """Immutable record of every case handler assignment/reassignment.

    FR-9: Tracks who was assigned, by whom, when, and under which ticket.
    """

    __tablename__ = "case_assignment_history"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(8), ForeignKey("cases.id"), nullable=False, index=True)
    from_user_id = Column(UUIDType(), ForeignKey("users.id"), nullable=True)
    to_user_id = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    ticket_id = Column(String(8), nullable=True)  # FR-8: reassignment via ticket
    assigned_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="assignments")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
