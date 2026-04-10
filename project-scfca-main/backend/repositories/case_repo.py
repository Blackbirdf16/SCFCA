"""Case repository — data access for Case and CaseAssignmentHistory models.

FR-5: Case creation with unique CaseID.
FR-6: Case assignment — one handler at a time.
FR-9: Immutable assignment history.
SR-17: Cases are never deleted.
"""

from __future__ import annotations

import random
import string
import uuid
from typing import Any, Sequence

from sqlalchemy.orm import Session

from backend.models.case import Case, CaseAssignmentHistory


def _generate_case_id() -> str:
    """Generate a random non-semantic CaseID like C-7A3F."""
    suffix = "".join(random.choices(string.digits + "ABCDEF", k=4))
    return f"C-{suffix}"


class CaseRepository:
    """Encapsulates all database operations for Case entities."""

    def create(
        self,
        db: Session,
        *,
        title: str,
        wallet_ref: str,
        handler_id: uuid.UUID,
        created_by: uuid.UUID,
    ) -> Case:
        case_id = _generate_case_id()
        # Ensure uniqueness (extremely unlikely collision)
        while db.query(Case).filter(Case.id == case_id).first():
            case_id = _generate_case_id()

        case = Case(
            id=case_id,
            title=title,
            wallet_ref=wallet_ref,
            handler_id=handler_id,
            custody_status="open",
            created_by=created_by,
        )
        db.add(case)

        # FR-9: Record initial assignment
        history = CaseAssignmentHistory(
            id=uuid.uuid4(),
            case_id=case_id,
            from_user_id=None,
            to_user_id=handler_id,
            ticket_id=None,
            assigned_by=created_by,
        )
        db.add(history)
        db.commit()
        db.refresh(case)
        return case

    def get_by_id(self, db: Session, case_id: str) -> Case | None:
        return db.query(Case).filter(Case.id == case_id.strip().upper()).first()

    def list_all(self, db: Session) -> Sequence[Case]:
        return db.query(Case).order_by(Case.created_at.desc()).all()

    def list_index(self, db: Session) -> list[dict[str, Any]]:
        """Return minimal case index (IDs + status only). FR-7."""
        cases = db.query(Case.id, Case.custody_status).order_by(Case.id).all()
        return [{"id": c.id, "custodyStatus": c.custody_status} for c in cases]

    def reassign(
        self,
        db: Session,
        *,
        case_id: str,
        new_handler_id: uuid.UUID,
        assigned_by: uuid.UUID,
        ticket_id: str | None = None,
    ) -> Case:
        """Reassign case handler and record in history. FR-8, FR-9."""
        case = self.get_by_id(db, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found")

        old_handler_id = case.handler_id
        case.handler_id = new_handler_id

        history = CaseAssignmentHistory(
            id=uuid.uuid4(),
            case_id=case.id,
            from_user_id=old_handler_id,
            to_user_id=new_handler_id,
            ticket_id=ticket_id,
            assigned_by=assigned_by,
        )
        db.add(history)
        db.commit()
        db.refresh(case)
        return case

    def get_assignment_history(self, db: Session, case_id: str) -> Sequence[CaseAssignmentHistory]:
        """Return assignment history for a case, newest first. FR-9."""
        return (
            db.query(CaseAssignmentHistory)
            .filter(CaseAssignmentHistory.case_id == case_id.strip().upper())
            .order_by(CaseAssignmentHistory.assigned_at.desc())
            .all()
        )


CASE_REPO = CaseRepository()
