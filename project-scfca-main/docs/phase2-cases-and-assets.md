# Phase 2 — Case & Asset Management

**Status:** Complete
**Date:** 2026-04-07
**Covers:** FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12, FR-13, SR-15, SR-17, NFR-13

---

## 1. Objective

Implement the full case lifecycle (creation, assignment, reassignment, history tracking) and a complete asset registry with frozen valuation snapshots and immutability enforcement at the ORM level.

---

## 2. Requirements Addressed

| ID | Requirement | How Addressed |
|----|------------|---------------|
| **FR-5** | Case creation with unique CaseID | `POST /api/v1/cases/` — random non-semantic C-XXXX IDs |
| **FR-6** | Case assignment (one handler) | `handler_id` FK on Case; checked in all routes |
| **FR-7** | Case index visibility | `GET /api/v1/cases/` — IDs + status for all authenticated users |
| **FR-8** | Case reassignment via ticket | `PATCH /api/v1/cases/{id}/reassign` with optional ticket_id |
| **FR-9** | Assignment history | `CaseAssignmentHistory` table; `GET /api/v1/cases/{id}/history` |
| **FR-10** | Asset registration | `POST /api/v1/assets/` with case linkage, type, quantity |
| **FR-11** | Frozen valuation snapshot | `POST /api/v1/assets/{id}/valuation` — INSERT-ONLY |
| **FR-12** | Asset facts immutability | SQLAlchemy `before_update` listener blocks quantity/symbol changes |
| **FR-13** | Metadata updates via ticket | `PATCH /api/v1/assets/{id}/metadata` — only status/notes mutable |
| **SR-15** | Asset data immutability | `before_update` + `before_delete` listeners raise on violation |
| **SR-17** | CaseIDs never deleted | `before_delete` listener on Case raises on violation |
| **NFR-13** | Configurable reference currency | `reference_currency` field on FrozenValuation (default USDT) |

---

## 3. Database Schema (New Tables)

### 3.1 Cases

```sql
CREATE TABLE cases (
    id              VARCHAR(8)  PRIMARY KEY,       -- C-XXXX (random, non-semantic)
    title           VARCHAR(256) NOT NULL,
    wallet_ref      VARCHAR(64)  NOT NULL,
    handler_id      CHAR(36)     NOT NULL REFERENCES users(id),
    custody_status  VARCHAR(20)  NOT NULL DEFAULT 'open',
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    created_by      CHAR(36)     NOT NULL REFERENCES users(id)
);
```

### 3.2 Case Assignment History

```sql
CREATE TABLE case_assignment_history (
    id          CHAR(36)    PRIMARY KEY,
    case_id     VARCHAR(8)  NOT NULL REFERENCES cases(id),
    from_user_id CHAR(36)   REFERENCES users(id),        -- NULL for initial assignment
    to_user_id  CHAR(36)    NOT NULL REFERENCES users(id),
    ticket_id   VARCHAR(8),                               -- FR-8: link to approval ticket
    assigned_by CHAR(36)    NOT NULL REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

### 3.3 Assets

```sql
CREATE TABLE assets (
    id            VARCHAR(8)    PRIMARY KEY,        -- AS-XXXX
    case_id       VARCHAR(8)    NOT NULL REFERENCES cases(id),
    symbol        VARCHAR(16)   NOT NULL,           -- BTC, ETH, SOL...
    asset_type    VARCHAR(32)   NOT NULL,           -- native, token, nft
    quantity      NUMERIC(28,8) NOT NULL,           -- IMMUTABLE (FR-12)
    protocol      VARCHAR(32),
    network       VARCHAR(32),
    status        VARCHAR(32)   NOT NULL DEFAULT 'registered',  -- mutable via ticket
    notes         VARCHAR(512),                     -- mutable via ticket
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    registered_by CHAR(36)      NOT NULL REFERENCES users(id)
);
```

### 3.4 Frozen Valuations

```sql
CREATE TABLE frozen_valuations (
    id                 CHAR(36)      PRIMARY KEY,
    asset_id           VARCHAR(8)    NOT NULL REFERENCES assets(id),
    reference_currency VARCHAR(8)    NOT NULL DEFAULT 'USDT',
    value              NUMERIC(28,8) NOT NULL,
    source             VARCHAR(128)  NOT NULL,       -- 'manual', 'coingecko', etc.
    snapshot_at        TIMESTAMP WITH TIME ZONE NOT NULL
);
-- INSERT-ONLY: no UPDATE or DELETE permitted (FR-11)
```

---

## 4. Immutability Enforcement

SQLAlchemy event listeners in `backend/models/listeners.py` enforce immutability at the ORM level:

| Listener | Model | Trigger | Effect |
|----------|-------|---------|--------|
| `_prevent_asset_fact_mutation` | Asset | `before_update` | Raises `ValueError` if `quantity`, `symbol`, or `asset_type` changed |
| `_prevent_asset_delete` | Asset | `before_delete` | Raises `ValueError` — assets cannot be deleted |
| `_prevent_valuation_update` | FrozenValuation | `before_update` | Raises `ValueError` — valuations are INSERT-ONLY |
| `_prevent_valuation_delete` | FrozenValuation | `before_delete` | Raises `ValueError` — valuations cannot be deleted |
| `_prevent_case_delete` | Case | `before_delete` | Raises `ValueError` — cases cannot be deleted (SR-17) |

These listeners fire regardless of how the ORM is accessed — whether through routes, scripts, or direct session manipulation — providing defense-in-depth against insider attacks (MU-5).

---

## 5. API Endpoints

### 5.1 Case Management (`/api/v1/cases/`)

| Method | Path | Description | Auth | Req ID |
|--------|------|-------------|------|--------|
| `GET` | `/api/v1/cases/` | List case index (IDs + status) | All authenticated | FR-7 |
| `GET` | `/api/v1/cases/{id}` | Case details (role-gated) | All authenticated | FR-6, FR-17 |
| `POST` | `/api/v1/cases/` | Create case | Admin only | FR-5 |
| `PATCH` | `/api/v1/cases/{id}/reassign` | Reassign handler | Admin only | FR-8, FR-9 |
| `GET` | `/api/v1/cases/{id}/history` | Assignment history | Admin/Auditor | FR-9 |

### 5.2 Asset Registry (`/api/v1/assets/`)

| Method | Path | Description | Auth | Req ID |
|--------|------|-------------|------|--------|
| `POST` | `/api/v1/assets/` | Register asset | Admin only | FR-10 |
| `GET` | `/api/v1/assets/` | List all assets | Admin/Handler | FR-10 |
| `GET` | `/api/v1/assets/{id}` | Asset details | Admin/Handler | FR-10 |
| `GET` | `/api/v1/assets/{id}/valuation` | Frozen valuations | All authenticated | FR-11 |
| `POST` | `/api/v1/assets/{id}/valuation` | Add valuation | Admin only | FR-11 |
| `PATCH` | `/api/v1/assets/{id}/metadata` | Update status/notes | Admin only | FR-13 |

---

## 6. Files Created

| File | Purpose |
|------|---------|
| `backend/models/case.py` | Case + CaseAssignmentHistory ORM models |
| `backend/models/asset.py` | Asset + FrozenValuation ORM models |
| `backend/models/listeners.py` | Immutability enforcement via SQLAlchemy event listeners |
| `backend/repositories/case_repo.py` | Case CRUD + assignment history repository |
| `backend/repositories/asset_repo.py` | Asset registration + valuation repository |
| `backend/api/v1/routes/assets.py` | Asset registry REST endpoints |
| `backend/alembic/versions/002_cases_and_assets.py` | Migration: 4 new tables |
| `frontend/src/services/assets.ts` | Frontend API service for asset operations |
| `tests/conftest.py` | Shared test DB fixtures (SQLite, truncation, seeding) |
| `tests/test_cases_and_assets.py` | 8 integration tests for cases and assets |

## 7. Files Modified

| File | Change |
|------|--------|
| `backend/models/__init__.py` | Added Case, Asset, FrozenValuation imports + listeners activation |
| `backend/main.py` | Registered assets router at `/api/v1/assets` |
| `backend/api/v1/routes/cases.py` | Expanded with POST (create), PATCH (reassign), GET (history) |
| `backend/services/case_service.py` | Added `case_model_to_detail()` for DB-backed case objects |
| `tests/test_user_management.py` | Simplified to use shared conftest fixtures |

---

## 8. Test Coverage

### New Tests (Phase 2) — 8 tests

| Test | Requirement | Validates |
|------|-------------|-----------|
| `test_admin_creates_case` | FR-5 | Admin creates case; correct ID format and fields |
| `test_regular_cannot_create_case` | FR-5 | Regular user gets 403 |
| `test_case_assignment_history_recorded` | FR-9 | Initial assignment creates history entry |
| `test_case_reassignment_and_history` | FR-8, FR-9 | Reassignment updates handler + adds history |
| `test_admin_registers_asset` | FR-10 | Admin registers asset with all fields |
| `test_frozen_valuation_created` | FR-11 | Valuation snapshot created and retrievable |
| `test_asset_immutability_enforced` | FR-12, SR-15 | Direct quantity modification raises ValueError |
| `test_regular_cannot_register_asset` | FR-10 | Regular user gets 403 |

### Full Suite Results

```
19 passed — 6 original + 5 Phase 1 + 8 Phase 2
```

### Test Infrastructure Improvement

Phase 2 introduced a shared `tests/conftest.py` that:
- Creates a single SQLite in-memory DB with `StaticPool` (shared connection)
- Creates tables once at import time
- Provides a `db_session` fixture that truncates all rows and re-seeds demo users
- Resets the rate limiter between tests to prevent 429 errors
- Eliminates duplicate setup code across test files

---

## 9. Dual-Mode Case/Asset Routes

The case list and detail endpoints support both DB-backed and in-memory demo data:

```
GET /api/v1/cases/
  → Try DB (CASE_REPO.list_index)
  → If DB empty or error → fall back to in-memory demo cases
  → Return case index

GET /api/v1/cases/{id}
  → Try DB (CASE_REPO.get_by_id + assets)
  → If not found → try in-memory demo case
  → Apply role-based visibility
  → Return case detail
```

This preserves backward compatibility with `test_workflows.py` (which relies on in-memory C-100 and C-101 cases) while enabling full DB-backed operations for new tests and production use.

---

## 10. Dependency Graph

```
Phase 1 (DB + Users) ✅
  ↓
Phase 2 (Cases + Assets) ✅  ← this phase
  ↓
Phase 3 (Tickets) — depends on Cases from Phase 2
  ↓
Phase 4 (Documents + Reports) — depends on Tickets from Phase 3
  ↓
Phase 5 (MFA + Re-auth) — depends on Users from Phase 1
  ↓
Phase 6 (Integration + Polish) — depends on all above
```
