"""Shared test fixtures for SCFCA integration tests.

Uses a single SQLite in-memory database with StaticPool.
Each test that needs DB gets fresh data via truncation + re-seed.
Rate limiters are reset before every test to prevent 429 cascades.
"""

from __future__ import annotations

from typing import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.main import app

import backend.models  # noqa: F401

# --- Single shared SQLite in-memory engine ---
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

# Create tables once at import time
Base.metadata.create_all(bind=TEST_ENGINE)


def override_get_db() -> Generator[Session, None, None]:
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def _truncate_all():
    """Delete all rows from all tables."""
    conn = TEST_ENGINE.connect()
    conn.execute(text("PRAGMA foreign_keys = OFF"))
    for table in reversed(Base.metadata.sorted_tables):
        conn.execute(table.delete())
    conn.execute(text("PRAGMA foreign_keys = ON"))
    conn.commit()
    conn.close()


def _seed_demo_users():
    """Seed the 4 demo users."""
    from passlib.context import CryptContext
    from backend.auth.schemas import Role
    from backend.models.user import User

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    conn = TEST_ENGINE.connect()
    session = Session(bind=conn)
    session.add_all([
        User(username="alice", password_hash=pwd.hash("alice123"), role=Role.regular, is_active=True),
        User(username="bob", password_hash=pwd.hash("bob123"), role=Role.administrator, is_active=True),
        User(username="eve", password_hash=pwd.hash("eve123"), role=Role.administrator, is_active=True),
        User(username="carol", password_hash=pwd.hash("carol123"), role=Role.auditor, is_active=True),
    ])
    session.commit()
    session.close()
    conn.close()


def _reset_all_rate_limiters():
    """Clear ALL rate limiters (login + general API) to avoid 429s across tests."""
    from backend.services import rate_limit
    if rate_limit.LOGIN_RATE_LIMITER is not None:
        rate_limit.LOGIN_RATE_LIMITER._events.clear()

    # Reset the general API rate limiters from middleware
    from backend.middleware.rate_limit import _read_limiter, _write_limiter
    _read_limiter._events.clear()
    _write_limiter._events.clear()


# Seed initial users so test_workflows.py (no db_session fixture) works
_seed_demo_users()


def _clear_mfa():
    """Clear MFA records to prevent state leaking between test files."""
    try:
        session = TestSession()
        session.execute(text("DELETE FROM user_mfa"))
        session.commit()
        session.close()
    except Exception:
        pass  # Table might not exist yet


@pytest.fixture(autouse=True)
def _reset_shared_state():
    """Reset rate limiters and MFA state before every test."""
    _reset_all_rate_limiters()
    _clear_mfa()
    yield


@pytest.fixture()
def db_session():
    """Provide fresh DB state: truncate all, re-seed demo users."""
    _truncate_all()
    _seed_demo_users()
    yield
