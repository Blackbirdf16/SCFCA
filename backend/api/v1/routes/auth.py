"""
Authentication endpoints for SCFCA backend (placeholder).
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/login", summary="User login", tags=["auth"])
def login():
    """Placeholder for user login endpoint."""
    return {"message": "Login endpoint (to be implemented)"}
