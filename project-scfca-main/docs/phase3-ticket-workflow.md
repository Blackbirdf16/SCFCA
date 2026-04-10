# Phase 3 — Complete Ticket Workflow

**Status:** Complete
**Date:** 2026-04-07
**Covers:** FR-8, FR-13, FR-15, FR-16, FR-18, FR-20, FR-27, SR-12, SR-13

---

## 1. Objective

Migrate the ticket system from in-memory storage to PostgreSQL, add all 6 ticket types, implement cancellation, enforce mandatory approval/rejection notes, and align the lifecycle states with the thesis specification — while preserving backward compatibility with the 19 existing tests.

---

## 2. Requirements Addressed

| ID | Requirement | How Addressed |
|----|------------|---------------|
| **FR-8** | Reassignment via approved ticket | `reassignment` ticket execution triggers `CASE_REPO.reassign()` with ticket_id reference |
| **FR-13** | Metadata updates via approved ticket | `metadata_correction` ticket execution triggers `ASSET_REPO.update_metadata()` |
| **FR-15** | All ticket types | 6 types: transfer_request, custody_change, release_request, conversion_request, reassignment, metadata_correction |
| **FR-16** | Ticket lifecycle | DB stores `open`/`in_process`/`closed` + `resolution`; display status maps to compat strings |
| **FR-18** | Mandatory notes | `notes` field on `TicketApproval`; stored and returned in approval history |
| **FR-20** | Ticket cancellation | `POST /tickets/{id}/cancel` — creator only, before finalization |
| **FR-27** | Transaction/action linking | `ticket_executions` table links execution to ticket with idempotency key |
| **SR-12** | Dual approval enforcement | Preserved — 2 distinct admin approvals required before execution |
| **SR-13** | Execution traceability | `TicketExecution` record with result, failure_reason, timestamps |

---

## 3. Database Schema (New Tables)

### 3.1 Tickets

```sql
CREATE TABLE tickets (
    id              VARCHAR(8)  PRIMARY KEY,
    case_id         VARCHAR(8)  NOT NULL REFERENCES cases(id),
    ticket_type     VARCHAR(32) NOT NULL,       -- 6 enum values
    description     TEXT        NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'open',     -- open/in_process/closed
    resolution      VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/approved/rejected/cancelled
    linked_doc_ids  JSON,
    parameters      JSON,                       -- structured params for reassignment/metadata
    created_by      CHAR(36)    NOT NULL REFERENCES users(id),
    assigned_to     CHAR(36)    REFERENCES users(id),
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    closed_at       TIMESTAMP WITH TIME ZONE
);
```

### 3.2 Ticket Approvals

```sql
CREATE TABLE ticket_approvals (
    id          CHAR(36)    PRIMARY KEY,
    ticket_id   VARCHAR(8)  NOT NULL REFERENCES tickets(id),
    stage       INTEGER     NOT NULL,           -- 1 or 2
    decision    VARCHAR(10) NOT NULL,           -- approved/rejected
    decided_by  CHAR(36)    NOT NULL REFERENCES users(id),
    notes       TEXT        NOT NULL,           -- FR-18: mandatory
    decided_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

### 3.3 Ticket Executions

```sql
CREATE TABLE ticket_executions (
    id               CHAR(36)     PRIMARY KEY,
    ticket_id        VARCHAR(8)   NOT NULL UNIQUE REFERENCES tickets(id),
    idempotency_key  VARCHAR(128) NOT NULL UNIQUE,
    executed_by      CHAR(36)     NOT NULL REFERENCES users(id),
    result           VARCHAR(64)  NOT NULL,
    failure_reason   TEXT,                       -- FR-28
    executed_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

---

## 4. Backward Compatibility — Display Status Mapping

| DB `status` | DB `resolution` | API `status` (display) | Used By |
|-------------|----------------|----------------------|---------|
| `open` | `pending` | `pending_review` | Existing tests + frontend |
| `in_process` | `pending` | `awaiting_second_approval` | Existing tests + frontend |
| `closed` | `approved` | `approved` | Existing tests + frontend |
| `closed` | `rejected` | `rejected` | Existing tests + frontend |
| `closed` | `cancelled` | `cancelled` | New in Phase 3 |

This mapping is implemented as a `display_status` property on the `Ticket` ORM model. All API responses use `display_status`, preserving the exact strings that `test_workflows.py` asserts.

---

## 5. Execution Side-Effects

| Ticket Type | Side-Effect | Traceability |
|-------------|-------------|--------------|
| `reassignment` | `CASE_REPO.reassign()` → handler changes, `CaseAssignmentHistory` created with `ticket_id` | FR-8, FR-9 |
| `metadata_correction` | `ASSET_REPO.update_metadata()` → asset notes/status updated | FR-13 |
| `release_request` | `ASSET_REPO.update_metadata(status="released")` | FR-10 |
| `transfer_request` | Simulated (logged only) | FR-27 |
| `custody_change` | Simulated (logged only) | FR-27 |
| `conversion_request` | Out-of-system (logged only) | FR-15 |

---

## 6. Files Created

| File | Purpose |
|------|---------|
| `backend/models/ticket.py` | Ticket, TicketApproval, TicketExecution ORM models with `display_status` |
| `backend/repositories/ticket_repo.py` | Full ticket CRUD, approval, cancel, execution |
| `backend/alembic/versions/003_tickets.py` | Migration: 3 new tables |
| `tests/test_tickets_phase3.py` | 8 integration tests |

## 7. Files Modified

| File | Change |
|------|--------|
| `backend/models/__init__.py` | Registered Ticket, TicketApproval, TicketExecution |
| `backend/api/v1/routes/tickets.py` | Full rewrite: DB-backed with legacy fallback, 6 types, cancel, notes, side-effects |
| `backend/services/case_service.py` | `is_case_assigned_to()` accepts optional `db` param for DB-aware check |
| `frontend/src/types/index.ts` | Added 3 ticket types + `cancelled` status + `notes` on approval events |
| `frontend/src/services/tickets.ts` | Added `cancel()`, updated `approve()`/`reject()` to accept notes |

---

## 8. Test Coverage

### New Tests (Phase 3) — 8 tests

| Test | Requirement | Validates |
|------|-------------|-----------|
| `test_ticket_cancellation_by_creator` | FR-20 | Handler cancels own open ticket → `cancelled` |
| `test_cancellation_blocked_after_full_approval` | FR-20 | Cancel on approved ticket → 409 |
| `test_non_creator_cannot_cancel` | FR-20 | Non-creator gets 403 |
| `test_notes_stored_in_approval_history` | FR-18 | Notes visible in approval history |
| `test_rejection_notes_stored` | FR-18 | Rejection notes stored and returned |
| `test_conversion_request_accepted` | FR-15 | New ticket type accepted |
| `test_reassignment_ticket_full_workflow` | FR-8, FR-15 | Full flow: create → approve → execute → handler changes |
| `test_metadata_correction_ticket_workflow` | FR-13, FR-15 | Full flow: create → approve → execute → notes updated |

### Full Suite

```
27 passed — 6 original + 5 Phase 1 + 8 Phase 2 + 8 Phase 3
```

---

## 9. Dual-Mode Architecture

Like Phases 1-2, ticket routes support both DB-backed and in-memory operation:

```
Request arrives
  → _use_db(db) checks if Ticket + User tables exist and are queryable
  → If yes: use TICKET_REPO (DB-backed, full features)
  → If no: use _LEGACY_TICKETS (in-memory, original behavior)
```

This ensures `test_workflows.py` (which has no `db_session` fixture) continues to use the in-memory fallback, while `test_tickets_phase3.py` (with `db_session`) tests the full DB-backed flow including side-effects.
