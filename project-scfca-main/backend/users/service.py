"""
User management service layer (placeholder).
Separates business logic from route logic for clarity and extensibility.
"""
from backend.users.schemas import UserCreate, UserRead
from typing import List

def create_user(user: UserCreate) -> UserRead:
    """Placeholder for user creation logic."""
    # TODO: Implement user creation with DB
    return UserRead(id=1, username=user.username, role=user.role, is_active=True)

def list_users() -> List[UserRead]:
    """Placeholder for user listing logic."""
    # TODO: Implement user listing from DB
    return []
