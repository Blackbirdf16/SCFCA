"""Tests for user management endpoints (Phase 1).

FR-1: Administrators can create and manage user profiles.
SR-4: Controlled role assignment — role changes are restricted and logged.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.main import app

USERS = {
    "alice": {"username": "alice", "password": "alice123"},
    "bob": {"username": "bob", "password": "bob123"},
    "eve": {"username": "eve", "password": "eve123"},
    "carol": {"username": "carol", "password": "carol123"},
}


@pytest.fixture(autouse=True)
def _db(db_session):
    """Use the shared DB fixture from conftest."""
    yield


def login(client: TestClient, username: str):
    resp = client.post("/api/v1/auth/login", json=USERS[username])
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    csrf = resp.cookies.get(settings.csrf_cookie_name)
    assert csrf
    return resp.cookies, csrf


def test_admin_creates_user():
    """FR-1: Admin can create a new user."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    resp = client.post(
        "/api/v1/users/",
        json={"username": "dave", "password": "dave123456", "role": "regular"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["username"] == "dave"
    assert data["role"] == "regular"
    assert data["is_active"] is True


def test_non_admin_cannot_create_user():
    """SR-4: Only admins can manage users."""
    client = TestClient(app)
    cookies, csrf = login(client, "alice")
    resp = client.post(
        "/api/v1/users/",
        json={"username": "mallory", "password": "mallory123", "role": "administrator"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 403


def test_admin_lists_users():
    """FR-1: Admin can list all users."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    resp = client.get("/api/v1/users/", cookies=cookies)
    assert resp.status_code == 200
    usernames = [u["username"] for u in resp.json()]
    assert "alice" in usernames
    assert "bob" in usernames


def test_duplicate_username_rejected():
    """FR-1: Cannot create user with existing username."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    resp = client.post(
        "/api/v1/users/",
        json={"username": "alice", "password": "newpass123", "role": "regular"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 409


def test_auditor_cannot_manage_users():
    """SR-4: Auditors have no user management access."""
    client = TestClient(app)
    cookies, csrf = login(client, "carol")
    resp = client.get("/api/v1/users/", cookies=cookies)
    assert resp.status_code == 403
