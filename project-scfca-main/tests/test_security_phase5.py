"""Tests for advanced security controls (Phase 5).

SR-5: MFA (TOTP) for privileged roles.
SR-6: Re-authentication for sensitive actions.
MU-9: General API rate limiting.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.main import app
from backend.services.mfa_service import get_current_code

USERS = {
    "alice": {"username": "alice", "password": "alice123"},
    "bob": {"username": "bob", "password": "bob123"},
    "eve": {"username": "eve", "password": "eve123"},
    "carol": {"username": "carol", "password": "carol123"},
}


@pytest.fixture(autouse=True)
def _db(db_session):
    yield


def login(client: TestClient, username: str):
    resp = client.post("/api/v1/auth/login", json=USERS[username])
    # MFA users get mfa_required instead of cookies
    if resp.status_code == 200 and resp.json().get("mfa_required"):
        return resp.cookies, None  # No CSRF for MFA-pending response
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    csrf = resp.cookies.get(settings.csrf_cookie_name)
    assert csrf, f"No CSRF cookie for {username}"
    return resp.cookies, csrf


def login_with_mfa(client: TestClient, username: str, password: str, totp_secret: str):
    """Login for a user who has MFA enabled. Returns cookies+csrf after full auth."""
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("mfa_required") is True, f"Expected MFA required but got: {data}"

    code = get_current_code(totp_secret)
    challenge = client.post(
        "/api/v1/auth/mfa/challenge",
        json={"mfa_token": data["mfa_token"], "code": code},
    )
    assert challenge.status_code == 200
    csrf = challenge.cookies.get(settings.csrf_cookie_name)
    return challenge.cookies, csrf


# ---------------------------------------------------------------------------
# SR-5: MFA Tests — create dedicated test admin user to avoid state leak
# ---------------------------------------------------------------------------

_mfa_user_counter = 0

def _create_mfa_test_user(client):
    """Create a unique temporary admin user for MFA testing. Returns (username, password)."""
    global _mfa_user_counter
    _mfa_user_counter += 1
    bob_cookies, bob_csrf = login(client, "bob")
    username = f"mfa_admin_{_mfa_user_counter}"
    password = "mfaTestPass123"
    resp = client.post(
        "/api/v1/users/",
        json={"username": username, "password": password, "role": "administrator"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    assert resp.status_code == 200, f"Failed to create MFA test user: {resp.text}"
    return username, password


def test_mfa_setup_and_enrollment():
    """SR-5: Admin can set up TOTP and verify to enable MFA."""
    client = TestClient(app)
    mfa_user, mfa_pass = _create_mfa_test_user(client)

    # Login as the MFA test user
    login_resp = client.post("/api/v1/auth/login", json={"username": mfa_user, "password": mfa_pass})
    assert login_resp.status_code == 200
    cookies = login_resp.cookies
    csrf = cookies.get(settings.csrf_cookie_name)

    setup = client.post("/api/v1/auth/mfa/setup", cookies=cookies, headers={"x-csrf-token": csrf})
    assert setup.status_code == 200
    data = setup.json()
    assert "secret" in data
    assert data["provisioning_uri"].startswith("otpauth://")

    code = get_current_code(data["secret"])
    verify = client.post(
        "/api/v1/auth/mfa/verify", json={"code": code},
        cookies=cookies, headers={"x-csrf-token": csrf},
    )
    assert verify.status_code == 200
    assert verify.json()["status"] == "mfa_enabled"


def test_mfa_login_requires_challenge():
    """SR-5: After MFA enabled, login returns mfa_required; challenge completes login."""
    client = TestClient(app)
    mfa_user, mfa_pass = _create_mfa_test_user(client)

    # Login and enable MFA
    login_resp = client.post("/api/v1/auth/login", json={"username": mfa_user, "password": mfa_pass})
    cookies = login_resp.cookies
    csrf = cookies.get(settings.csrf_cookie_name)

    setup = client.post("/api/v1/auth/mfa/setup", cookies=cookies, headers={"x-csrf-token": csrf})
    secret = setup.json()["secret"]
    code = get_current_code(secret)
    client.post("/api/v1/auth/mfa/verify", json={"code": code}, cookies=cookies, headers={"x-csrf-token": csrf})
    client.post("/api/v1/auth/logout", cookies=cookies, headers={"x-csrf-token": csrf})

    # Login again — should require MFA
    login_resp2 = client.post("/api/v1/auth/login", json={"username": mfa_user, "password": mfa_pass})
    data = login_resp2.json()
    assert data.get("mfa_required") is True, f"Expected mfa_required but got: {data}"

    # Complete MFA challenge
    mfa_code = get_current_code(secret)
    challenge = client.post(
        "/api/v1/auth/mfa/challenge",
        json={"mfa_token": data["mfa_token"], "code": mfa_code},
    )
    assert challenge.status_code == 200
    assert challenge.json()["username"] == mfa_user


def test_mfa_wrong_code_rejected():
    """SR-5: Invalid TOTP code is rejected during verification."""
    client = TestClient(app)
    mfa_user, mfa_pass = _create_mfa_test_user(client)

    login_resp = client.post("/api/v1/auth/login", json={"username": mfa_user, "password": mfa_pass})
    cookies = login_resp.cookies
    csrf = cookies.get(settings.csrf_cookie_name)

    client.post("/api/v1/auth/mfa/setup", cookies=cookies, headers={"x-csrf-token": csrf})

    verify = client.post(
        "/api/v1/auth/mfa/verify", json={"code": "000000"},
        cookies=cookies, headers={"x-csrf-token": csrf},
    )
    assert verify.status_code == 401


def test_non_admin_cannot_setup_mfa():
    """SR-5: MFA setup is restricted to administrator role."""
    client = TestClient(app)
    cookies, csrf = login(client, "alice")
    resp = client.post("/api/v1/auth/mfa/setup", cookies=cookies, headers={"x-csrf-token": csrf})
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# SR-6: Re-Authentication Tests — use bob (no MFA enabled)
# ---------------------------------------------------------------------------

def test_reauth_required_for_execution():
    """SR-6: Ticket execution without reauth token returns 403."""
    client = TestClient(app)
    bob_cookies, bob_csrf = login(client, "bob")

    case = client.post(
        "/api/v1/cases/",
        json={"title": "Reauth test", "wallet_ref": "WLT-REAUTH", "handler_username": "alice"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    ).json()["case"]

    alice_cookies, alice_csrf = login(client, "alice")
    ticket = client.post(
        "/api/v1/tickets/",
        json={"caseId": case["id"], "ticketType": "transfer_request", "description": "Test"},
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
    ).json()["ticket"]

    # Dual approve
    bob_cookies, bob_csrf = login(client, "bob")
    client.post(f"/api/v1/tickets/{ticket['id']}/approve", json={"notes": "ok"},
                cookies=bob_cookies, headers={"x-csrf-token": bob_csrf})
    eve_cookies, eve_csrf = login(client, "eve")
    client.post(f"/api/v1/tickets/{ticket['id']}/approve", json={"notes": "ok"},
                cookies=eve_cookies, headers={"x-csrf-token": eve_csrf})

    # Assign
    bob_cookies, bob_csrf = login(client, "bob")
    client.patch(f"/api/v1/tickets/{ticket['id']}/assign",
                 json={"assignedTo": "bob"}, cookies=bob_cookies, headers={"x-csrf-token": bob_csrf})

    # Execute WITHOUT reauth → 403
    exec_resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/execute",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf, "Idempotency-Key": "no-reauth-key"},
    )
    assert exec_resp.status_code == 403
    assert "Re-authentication" in exec_resp.json()["detail"]


def test_reauth_with_wrong_password():
    """SR-6: Reauth with wrong password returns 401."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    resp = client.post(
        "/api/v1/auth/reauth", json={"password": "wrongpassword"},
        cookies=cookies, headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 401


def test_reauth_success():
    """SR-6: Reauth with correct password returns a valid token."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    resp = client.post(
        "/api/v1/auth/reauth", json={"password": "bob123"},
        cookies=cookies, headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 200
    assert "reauth_token" in resp.json()
