"""
SQLAlchemy User model skeleton for SCFCA.
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum
from backend.core.database import Base
from backend.auth.schemas import Role

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    is_active = Column(Boolean, default=True)
