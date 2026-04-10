# SCFCA Documentation

> Secure Custody Framework for Cryptocurrency Assets — Master's Thesis PoC

---

## How to Use This Project

| I want to... | Read this |
|--------------|-----------|
| Run the app | [Root README](../README.md) |
| Run the tests | [Testing Guide](testing-guide.md) |
| Understand what was built | [Implementation Record](implementation-record.md) |
| Trace a requirement to code | [Traceability Matrix](traceability-matrix.md) |

---

## Implementation Phases

| Phase | Document | What It Covers |
|-------|----------|---------------|
| 1 | [Database & User Management](phase1-database-and-user-management.md) | PostgreSQL, Alembic, user CRUD, repository pattern |
| 2 | [Cases & Assets](phase2-cases-and-assets.md) | Case lifecycle, asset registry, immutability enforcement |
| 3 | [Ticket Workflow](phase3-ticket-workflow.md) | 6 ticket types, cancellation, mandatory notes, side-effects |
| 4 | [Documents & Reports](phase4-documents-and-reports.md) | PDF persistence, server-side report generation |
| 5 | [Advanced Security](phase5-advanced-security.md) | TOTP MFA, re-authentication, API rate limiting |
| 6 | [Integration & Polish](phase6-integration-and-polish.md) | Traceability matrix, CI/CD, final documentation |

---

## Coverage

```
29/29 Functional Requirements   (FR-1 to FR-29)
20/20 Security Requirements     (SR-1 to SR-20)
 9/9  Misuse Cases Mitigated    (MU-1 to MU-9)
  41  Integration Tests Passing
```
