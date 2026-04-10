"""User ORM model for SCFCA.

FR-1: User account management — administrators can create and manage user profiles.
FR-2: Pseudonymous UserIDs — the id column is a UUID, not tied to real identity.
SR-4: Controlled role assignment — role changes are restricted and logged.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String
from sqlalchemy.types import TypeDecorator, CHAR

from backend.auth.schemas import Role
from backend.core.database import Base
from backend.models.base import TimestampMixin


class UUIDType(TypeDecorator):
    """Platform-independent UUID type.

    Uses CHAR(32) for SQLite and native UUID for PostgreSQL.
    """

    impl = CHAR
    cache_ok = True

    def __init__(self) -> None:
        super().__init__(length=36)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum(Role, name="role_enum", create_constraint=False, native_enum=False), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(UUIDType(), ForeignKey("users.id"), nullable=True)
