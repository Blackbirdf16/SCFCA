# Phase 1 — Database Foundation & User Management

**Status:** Complete
**Date:** 2026-04-06
**Covers:** FR-1, FR-2, SR-4, SR-9, SR-10, SR-11, SR-17, NFR-4

---

## 1. Objective

Replace all in-memory data stores with PostgreSQL persistence and implement full user account management (CRUD) restricted to administrators. This phase establishes the foundation that every subsequent phase depends on: a real database, a repository abstraction layer, Alembic migrations, and a Docker-composed PostgreSQL service.

---

## 2. Requirements Addressed

| ID | Requirement | How Addressed |
|----|------------|---------------|
| **FR-1** | User account management | `POST/GET/PATCH/DELETE /api/v1/users/` — admin-only CRUD |
| **FR-2** | Pseudonymous User IDs | User PK is a UUID (not sequential int, not username) |
| **SR-4** | Controlled role assignment | Role changes restricted to administrators, fully audit-logged |
| **SR-9** | Tamper-evident audit logs | `AuditEventRecord` ORM model with SHA-256 hash chaining |
| **SR-10** | Log deletion prevention | Audit repository exposes INSERT only — no update/delete |
| **SR-11** | Non-repudiation | Every audit event tied to a pseudonymous `actor_id` |
| **SR-17** | Case ID persistence | Database-backed storage — data survives restarts |
| **NFR-4** | Long-term data retention | PostgreSQL with persistent Docker volume (`pgdata`) |

---

## 3. Architecture Decisions

### 3.1 Dual-Mode Authentication

The auth layer tries the **database first**, then falls back to **hardcoded demo users**. This preserves full backward compatibility with the original 6 integration tests (which run without a database) while enabling real DB-backed auth when PostgreSQL is available.

```
Login request
  → Try DB lookup (UserRepository.get_by_username)
  → If DB unavailable or user not found in DB → try demo users dict
  → If neither → 401 Unauthorized
```

**Rationale:** The existing test suite (`test_workflows.py`) relies on in-memory demo users and has no database dependency. Breaking those tests would regress security controls that are already validated. The fallback approach lets both modes coexist.

### 3.2 Repository Pattern

All database access goes through repository classes, not direct ORM queries in route handlers. This provides:

- **Testability** — repositories can be mocked or swapped for test doubles
- **Separation of concerns** — routes handle HTTP, repositories handle SQL
- **Consistency** — all queries for an entity live in one place

```
Route Handler → Repository → SQLAlchemy Session → PostgreSQL
```

### 3.3 Platform-Independent UUID Type

The `User.id` column uses a custom `UUIDType` (TypeDecorator) that stores UUIDs as `CHAR(36)` on SQLite and native UUID on PostgreSQL. This allows the same models to work in both test (SQLite in-memory) and production (PostgreSQL) environments without conditional logic.

### 3.4 SQLite-Compatible JSON

The `AuditEventRecord.details` column uses `sqlalchemy.JSON` instead of `postgresql.JSONB`. PostgreSQL handles `JSON` efficiently, and this avoids SQLite test failures since SQLite has no JSONB support.

### 3.5 Enum Without Native Type

The `User.role` column uses `Enum(Role, native_enum=False, create_constraint=False)` to store roles as VARCHAR strings rather than PostgreSQL-native enums. This simplifies cross-database testing and avoids migration headaches when adding new roles in the future.

---

## 4. Database Schema

### 4.1 Users Table

```sql
CREATE TABLE users (
    id          CHAR(36)     PRIMARY KEY,        -- UUID
    username    VARCHAR(64)  UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role        VARCHAR(13)  NOT NULL,            -- regular|administrator|auditor
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by  CHAR(36)     REFERENCES users(id),
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at  TIMESTAMP WITH TIME ZONE
);
```

### 4.2 Audit Events Table

```sql
CREATE TABLE audit_events (
    id          VARCHAR(12)  PRIMARY KEY,         -- AU-XXXXXX
    timestamp   TIMESTAMP WITH TIME ZONE NOT NULL,
    actor_id    VARCHAR(24)  NOT NULL,            -- pseudonymous hash
    event_type  VARCHAR(32)  NOT NULL,
    action      VARCHAR(64)  NOT NULL,
    entity_type VARCHAR(32),
    entity_id   VARCHAR(64),
    details     JSON,
    prev_hash   VARCHAR(64),
    hash        VARCHAR(64)  NOT NULL UNIQUE       -- SHA-256
);

CREATE INDEX ix_audit_events_entity ON audit_events(entity_type, entity_id);
CREATE INDEX ix_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX ix_audit_events_actor_id ON audit_events(actor_id);
CREATE INDEX ix_audit_events_event_type ON audit_events(event_type);
```

---

## 5. API Endpoints Added

### 5.1 User Management (`/api/v1/users/`)

All endpoints require the `administrator` role. All actions are audit-logged.

| Method | Path | Description | Auth | Req ID |
|--------|------|-------------|------|--------|
| `POST` | `/api/v1/users/` | Create a new user | Admin only | FR-1, SR-4 |
| `GET` | `/api/v1/users/` | List all active users | Admin only | FR-1 |
| `PATCH` | `/api/v1/users/{id}/role` | Change a user's role | Admin only | SR-4 |
| `DELETE` | `/api/v1/users/{id}` | Deactivate a user (soft delete) | Admin only | FR-1 |

#### Request/Response Schemas

**Create User** — `POST /api/v1/users/`
```json
// Request
{
  "username": "dave",           // 2-64 chars, unique
  "password": "dave123456",     // 6-128 chars
  "role": "regular"             // regular | administrator | auditor
}

// Response (200)
{
  "id": "a1b2c3d4-...",
  "username": "dave",
  "role": "regular",
  "is_active": true
}

// Error (409)
{ "detail": "Username already exists" }
```

**List Users** — `GET /api/v1/users/`
```json
// Response (200)
[
  { "id": "...", "username": "alice", "role": "regular", "is_active": true },
  { "id": "...", "username": "bob", "role": "administrator", "is_active": true }
]
```

**Change Role** — `PATCH /api/v1/users/{id}/role`
```json
// Request
{ "role": "auditor" }

// Response (200)
{ "id": "...", "username": "alice", "role": "auditor", "is_active": true }
```

**Deactivate User** — `DELETE /api/v1/users/{id}`
```json
// Response (200)
{ "id": "...", "username": "dave", "role": "regular", "is_active": false }
```

---

## 6. Files Created

| File | Purpose |
|------|---------|
| `backend/models/__init__.py` | Model registry — imports all ORM models so Alembic can discover them |
| `backend/models/base.py` | `TimestampMixin` providing `created_at` and `updated_at` columns |
| `backend/models/user.py` | `User` ORM model with UUID PK, bcrypt hash, role enum |
| `backend/models/audit_event.py` | `AuditEventRecord` ORM model with SHA-256 hash chain columns |
| `backend/repositories/__init__.py` | Repository package marker |
| `backend/repositories/user_repo.py` | `UserRepository` — create, get_by_username, list, update_role, deactivate |
| `backend/repositories/audit_repo.py` | `AuditRepository` — append (hash-chained), list, verify_chain |
| `backend/api/v1/routes/users.py` | User management REST endpoints (admin-only CRUD) |
| `backend/alembic.ini` | Alembic configuration (reads DATABASE_URL from app settings) |
| `backend/alembic/env.py` | Alembic environment — imports models, overrides URL from settings |
| `backend/alembic/script.py.mako` | Migration script template |
| `backend/alembic/versions/001_initial_schema.py` | Initial migration: `users` + `audit_events` tables |
| `tests/test_user_management.py` | 5 integration tests for user CRUD and access control |

---

## 7. Files Modified

| File | Change | Why |
|------|--------|-----|
| `backend/main.py` | Added `users` router import and registration at `/api/v1/users` | Wire up new endpoints |
| `backend/api/v1/routes/auth.py` | DB-first authentication with demo user fallback | FR-1: real user lookup; backward compat for tests |
| `backend/auth/dependencies.py` | Added `from __future__ import annotations` | Python 3.9 compatibility (`str \| None` syntax) |
| `backend/users/models.py` | Re-exports `User` from `backend.models.user` | Backward compatibility with existing imports |
| `backend/users/schemas.py` | Updated to Pydantic v2 with UUID id, added `UserRoleUpdate` | Match new DB model |
| `backend/requirements.txt` | Added `alembic`, `eval_type_backport` | Migrations + Python 3.9 type syntax support |
| `docker-compose.yml` | Added `postgres:16-alpine` service with healthcheck + volume | NFR-4: persistent storage |
| `scripts/seed_demo_data.py` | Rewrote to use new ORM models and create tables properly | Was broken (referenced undefined models) |

---

## 8. Docker Compose Changes

### Before (2 services)
```
backend → port 8000
frontend → port 5173
```

### After (3 services)
```
postgres → port 5432 (postgres:16-alpine, healthcheck, persistent volume)
backend  → port 8000 (depends_on postgres healthy, DATABASE_URL injected)
frontend → port 5173 (depends_on backend healthy)
```

### New Environment Variable
```
DATABASE_URL=postgresql://scfca:scfca@postgres:5432/scfca
```

### Persistent Volume
```yaml
volumes:
  pgdata:  # survives docker-compose down, preserves all data
```

---

## 9. Test Coverage

### Existing Tests (Unchanged, Still Passing)

| Test | What It Validates |
|------|-------------------|
| `test_login_sets_cookie_and_me_works` | JWT cookie auth flow |
| `test_csrf_blocks_unsafe_without_header` | CSRF double-submit enforcement |
| `test_ticket_dual_approval_execution_idempotency_and_replay_protection` | Full dual-approval + idempotency + replay denial |
| `test_document_pdf_only_upload_and_verify_integrity` | PDF validation + SHA-256 integrity |
| `test_regular_cannot_upload_for_unassigned_case` | Case assignment RBAC |
| `test_audit_hash_chain_verifies` | Audit log hash chain integrity |

### New Tests (Phase 1)

| Test | Requirement | What It Validates |
|------|-------------|-------------------|
| `test_admin_creates_user` | FR-1 | Admin can create user via API; correct response shape |
| `test_non_admin_cannot_create_user` | SR-4 | Regular user gets 403 on user creation |
| `test_admin_lists_users` | FR-1 | Admin can list all seeded users |
| `test_duplicate_username_rejected` | FR-1 | Creating existing username returns 409 |
| `test_auditor_cannot_manage_users` | SR-4 | Auditor gets 403 on user list |

### Test Infrastructure

The new tests use **SQLite in-memory** with `StaticPool` to avoid requiring a running PostgreSQL instance. A `setup_db` fixture creates tables and seeds demo users before each test, then drops everything after.

```python
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

The FastAPI dependency override ensures route handlers receive the test DB session:
```python
app.dependency_overrides[get_db] = override_get_db
```

### Running Tests

```bash
# All tests (11 total)
python3 -m pytest tests/ -q

# Only existing workflow tests (6)
python3 -m pytest tests/test_workflows.py -q

# Only new user management tests (5)
python3 -m pytest tests/test_user_management.py -q
```

**Result: 11 passed, 0 failed.**

---

## 10. Audit Trail for User Management

Every user management action generates an audit event with full traceability:

| Action | Event Type | Audit Action | Details |
|--------|-----------|--------------|---------|
| Create user | `admin` | `user_created` | role, created_by |
| Change role | `admin` | `role_changed` | old_role, new_role, changed_by |
| Deactivate user | `admin` | `user_deactivated` | deactivated_by |

All `actor_id` values are pseudonymous (HMAC-SHA256 derived from username + secret key), preserving SR-20.

---

## 11. Migration Guide

### Local Development (without Docker)

```bash
# 1. Start PostgreSQL (if not using Docker)
# 2. Set environment variable
export DATABASE_URL=postgresql://scfca:scfca@localhost:5432/scfca

# 3. Run migrations
cd backend && alembic upgrade head

# 4. Seed demo data
python scripts/seed_demo_data.py

# 5. Start backend
uvicorn backend.main:app --reload
```

### Docker Compose

```bash
# Everything starts automatically — postgres, backend, frontend
docker-compose up --build

# Seed data (in a separate terminal)
docker-compose exec backend python scripts/seed_demo_data.py
```

---

## 12. Known Limitations

| Limitation | Impact | Resolution Plan |
|-----------|--------|-----------------|
| Auth still falls back to in-memory demo users when DB is unavailable | Tests work without DB; production should always have DB | Phase 6 will add startup DB health check |
| Audit events from existing routes still use in-memory `AUDIT_LOG` singleton | In-memory audit events lost on restart for non-user-management routes | Phases 2-4 will migrate remaining routes to DB-backed audit |
| `created_by` on User is always `None` | Cannot link who created whom (would need principal UUID lookup) | Phase 2 will add principal-to-UUID resolution |
| No password complexity validation beyond min length 6 | Weak passwords possible in PoC | Acceptable for thesis PoC scope |

---

## 13. Dependency Graph

```
Phase 1 (this phase)
  ├── PostgreSQL + Alembic + ORM models
  ├── User Repository + Audit Repository
  ├── User Management API (admin CRUD)
  └── 11 passing tests (6 existing + 5 new)
       ↓
Phase 2 (Cases + Assets) — depends on DB + User model from Phase 1
       ↓
Phase 3 (Tickets) — depends on Cases from Phase 2
       ↓
Phase 4 (Documents + Reports) — depends on Tickets from Phase 3
       ↓
Phase 5 (MFA + Re-auth) — depends on Users from Phase 1
       ↓
Phase 6 (Integration + Polish) — depends on all above
```
