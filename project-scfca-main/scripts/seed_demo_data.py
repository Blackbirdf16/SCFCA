"""SCFCA: Database seeder for demo data.

Creates tables and seeds demo users for the proof of concept.
Passwords are for demonstration purposes only.

Usage:
    python -m scripts.seed_demo_data
    # or from project root:
    python scripts/seed_demo_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passlib.context import CryptContext

from backend.auth.schemas import Role
from backend.core.database import Base, SessionLocal, engine

# Import all models so Base.metadata knows about them
import backend.models  # noqa: F401

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed() -> None:
    """Drop and recreate all tables, then insert demo users."""
    from backend.models.user import User

    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # --- Demo Users (FR-1) ---
        demo_users = [
            User(
                username="alice",
                password_hash=pwd_context.hash("alice123"),
                role=Role.regular,
                is_active=True,
            ),
            User(
                username="bob",
                password_hash=pwd_context.hash("bob123"),
                role=Role.administrator,
                is_active=True,
            ),
            User(
                username="eve",
                password_hash=pwd_context.hash("eve123"),
                role=Role.administrator,
                is_active=True,
            ),
            User(
                username="carol",
                password_hash=pwd_context.hash("carol123"),
                role=Role.auditor,
                is_active=True,
            ),
        ]

        db.add_all(demo_users)
        db.commit()

        for u in demo_users:
            db.refresh(u)
            print(f"  Seeded user: {u.username} ({u.role.value})")

        print(f"\nDone. {len(demo_users)} users seeded.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
