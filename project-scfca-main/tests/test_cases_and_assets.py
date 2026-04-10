"""Tests for case management and asset registry (Phase 2).

FR-5:  Case creation (admin only).
FR-6:  Case assignment — handler sees only assigned cases.
FR-9:  Assignment history tracking.
FR-10: Asset registration.
FR-11: Frozen valuation snapshot.
FR-12: Asset facts immutability.
SR-15: Asset data immutability.
SR-17: Cases cannot be deleted.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.main import app
from tests.conftest import TestSession

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


# ---------------------------------------------------------------------------
# Case Tests
# ---------------------------------------------------------------------------

def test_admin_creates_case():
    """FR-5: Admin can create a new custody case."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    resp = client.post(
        "/api/v1/cases/",
        json={"title": "Seized BTC wallet", "wallet_ref": "WLT-TEST-001", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 200, resp.text
    case = resp.json()["case"]
    assert case["title"] == "Seized BTC wallet"
    assert case["handler"] == "alice"
    assert case["custodyStatus"] == "open"
    assert case["id"].startswith("C-")


def test_regular_cannot_create_case():
    """FR-5: Only admins can create cases."""
    client = TestClient(app)
    cookies, csrf = login(client, "alice")
    resp = client.post(
        "/api/v1/cases/",
        json={"title": "Unauthorized", "wallet_ref": "WLT-X", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 403


def test_case_assignment_history_recorded():
    """FR-9: Creating a case records the initial assignment."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")
    create = client.post(
        "/api/v1/cases/",
        json={"title": "History test", "wallet_ref": "WLT-HIST", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    case_id = create.json()["case"]["id"]

    history = client.get(f"/api/v1/cases/{case_id}/history", cookies=cookies)
    assert history.status_code == 200
    entries = history.json()["history"]
    assert len(entries) >= 1
    assert entries[0]["fromUser"] is None  # Initial assignment


def test_case_reassignment_and_history():
    """FR-8, FR-9: Admin can reassign handler; history is tracked."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")

    create = client.post(
        "/api/v1/cases/",
        json={"title": "Reassign test", "wallet_ref": "WLT-REASSIGN", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    case_id = create.json()["case"]["id"]

    reassign = client.patch(
        f"/api/v1/cases/{case_id}/reassign",
        json={"new_handler_username": "eve"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert reassign.status_code == 200
    assert reassign.json()["newHandler"] == "eve"

    history = client.get(f"/api/v1/cases/{case_id}/history", cookies=cookies)
    assert len(history.json()["history"]) == 2


# ---------------------------------------------------------------------------
# Asset Tests
# ---------------------------------------------------------------------------

def test_admin_registers_asset():
    """FR-10: Admin can register a seized asset under a case."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")

    case = client.post(
        "/api/v1/cases/",
        json={"title": "Asset test", "wallet_ref": "WLT-ASSET", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    ).json()["case"]

    resp = client.post(
        "/api/v1/assets/",
        json={"caseId": case["id"], "symbol": "BTC", "assetType": "native", "quantity": 12.5,
              "protocol": "bitcoin", "network": "mainnet"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 200, resp.text
    asset = resp.json()["asset"]
    assert asset["symbol"] == "BTC"
    assert asset["quantity"] == 12.5
    assert asset["id"].startswith("AS-")


def test_frozen_valuation_created():
    """FR-11: Admin can create a frozen valuation snapshot."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")

    case = client.post(
        "/api/v1/cases/",
        json={"title": "Valuation test", "wallet_ref": "WLT-VAL", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    ).json()["case"]

    asset = client.post(
        "/api/v1/assets/",
        json={"caseId": case["id"], "symbol": "ETH", "assetType": "native", "quantity": 100.0},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    ).json()["asset"]

    val = client.post(
        f"/api/v1/assets/{asset['id']}/valuation",
        json={"value": 350000.00, "referenceCurrency": "USDT", "source": "manual"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert val.status_code == 200, val.text
    v = val.json()["valuation"]
    assert v["value"] == 350000.0
    assert v["referenceCurrency"] == "USDT"

    vals = client.get(f"/api/v1/assets/{asset['id']}/valuation", cookies=cookies)
    assert len(vals.json()["valuations"]) == 1


def test_asset_immutability_enforced():
    """FR-12, SR-15: Asset quantity cannot be modified after registration."""
    client = TestClient(app)
    cookies, csrf = login(client, "bob")

    case = client.post(
        "/api/v1/cases/",
        json={"title": "Immutability test", "wallet_ref": "WLT-IMM", "handler_username": "alice"},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    ).json()["case"]

    asset = client.post(
        "/api/v1/assets/",
        json={"caseId": case["id"], "symbol": "SOL", "assetType": "native", "quantity": 500.0},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    ).json()["asset"]

    from backend.models.asset import Asset
    db = TestSession()
    db_asset = db.query(Asset).filter(Asset.id == asset["id"]).first()
    assert db_asset is not None

    with pytest.raises(ValueError, match="SR-15/FR-12 violation"):
        db_asset.quantity = 9999
        db.commit()
    db.rollback()
    db.close()


def test_regular_cannot_register_asset():
    """FR-10: Only admins can register assets."""
    client = TestClient(app)
    cookies, csrf = login(client, "alice")
    resp = client.post(
        "/api/v1/assets/",
        json={"caseId": "C-FAKE", "symbol": "BTC", "assetType": "native", "quantity": 1.0},
        cookies=cookies,
        headers={"x-csrf-token": csrf},
    )
    assert resp.status_code == 403
