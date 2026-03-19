"""
Pydantic schemas for user representation.
"""
from pydantic import BaseModel
from backend.auth.schemas import Role

class UserBase(BaseModel):
    username: str
    role: Role
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    role: Role
    is_active: bool
