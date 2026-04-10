"""
Authentication service layer for SCFCA PoC.
Verifies password hashes and fetches user from DB.
"""
from backend.core.database import SessionLocal
from backend.core.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None
