"""
User management API routes (placeholder).
"""
from fastapi import APIRouter
from backend.users.schemas import UserCreate, UserRead
from backend.users.service import create_user, list_users
from typing import List

router = APIRouter()

@router.post("/", response_model=UserRead, summary="Create user")
def create(user: UserCreate):
    """Create a new user (placeholder)."""
    return create_user(user)

@router.get("/", response_model=List[UserRead], summary="List users")
def get_users():
    """List all users (placeholder)."""
    return list_users()
