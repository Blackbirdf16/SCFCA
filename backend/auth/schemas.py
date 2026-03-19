"""
Pydantic schemas for authentication and RBAC roles.
"""
from pydantic import BaseModel
from enum import Enum

class Role(str, Enum):
    case_handler = "case_handler"
    administrator = "administrator"
    auditor = "auditor"

class LoginRequest(BaseModel):
    username: str
    password: str
