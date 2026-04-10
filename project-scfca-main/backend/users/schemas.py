"""Pydantic schemas for user management endpoints.

FR-1: User account management.
SR-4: Controlled role assignment.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from backend.auth.schemas import Role


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    role: Role


class UserRead(BaseModel):
    id: UUID
    username: str
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: Role
