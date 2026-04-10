"""
Pydantic schemas for authentication and RBAC roles.
"""
from pydantic import BaseModel
from enum import Enum

class Role(str, Enum):
    regular = "regular"
    administrator = "administrator"
    auditor = "auditor"

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: Role


class MeResponse(BaseModel):
    username: str
    role: Role
