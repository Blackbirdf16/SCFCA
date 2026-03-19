"""
Authentication API routes (placeholder).
"""
from fastapi import APIRouter, HTTPException, status
from backend.auth.schemas import LoginRequest
from backend.auth.service import authenticate_user

router = APIRouter()

@router.post("/login", summary="User login")
def login(request: LoginRequest):
    """Authenticate user and return access token (TODO: implement real logic)."""
    # TODO: Implement authentication and token generation
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Login not implemented yet.")
