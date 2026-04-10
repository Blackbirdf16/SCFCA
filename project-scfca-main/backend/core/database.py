"""
Database setup for SCFCA backend.
Defines SQLAlchemy engine, session, Base, and get_db dependency for ORM integration.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import settings
from typing import Generator

# SQLAlchemy engine and session
engine = create_engine(settings.database_url, echo=settings.debug, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()

def get_db() -> Generator:
	"""Dependency that provides a SQLAlchemy session and ensures cleanup."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
