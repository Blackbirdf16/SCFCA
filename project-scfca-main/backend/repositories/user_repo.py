"""User repository — data access for User model.

FR-1: User account management.
SR-4: Controlled role assignment — all role changes go through this layer.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy.orm import Session

from backend.auth.schemas import Role
from backend.models.user import User


class UserRepository:
    """Encapsulates all database operations for the User entity."""

    def create(
        self,
        db: Session,
        *,
        username: str,
        password_hash: str,
        role: Role,
        created_by: uuid.UUID | None = None,
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            username=username.strip().lower(),
            password_hash=password_hash,
            role=role,
            is_active=True,
            created_by=created_by,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_username(self, db: Session, username: str) -> User | None:
        return (
            db.query(User)
            .filter(User.username == username.strip().lower())
            .first()
        )

    def get_by_id(self, db: Session, user_id: uuid.UUID) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def list_all(self, db: Session, *, active_only: bool = True) -> Sequence[User]:
        q = db.query(User)
        if active_only:
            q = q.filter(User.is_active == True)  # noqa: E712
        return q.order_by(User.username).all()

    def update_role(self, db: Session, user_id: uuid.UUID, new_role: Role) -> User | None:
        user = self.get_by_id(db, user_id)
        if user is None:
            return None
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, user_id: uuid.UUID) -> User | None:
        user = self.get_by_id(db, user_id)
        if user is None:
            return None
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user


# Module-level singleton for convenience.
USER_REPO = UserRepository()
