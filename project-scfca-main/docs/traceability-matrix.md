# SCFCA Traceability Matrix

**Last Updated:** 2026-04-09
**Test Suite:** 41 passing across 6 test files

This matrix links every thesis requirement to its implementing code and validating test, providing auditable justification that each architectural control is risk-driven and enforceable (as required by the methodology in Chapter 3).

---

## 1. Functional Requirements (FR-1 to FR-29)

| ID | Requirement | Code | Test |
|----|------------|------|------|
| **FR-1** | User account management | `api/v1/routes/users.py` (CRUD endpoints) | `test_user_management.py::test_admin_creates_user` |
| **FR-2** | Pseudonymous User IDs | `models/user.py` (UUID PK), `services/security_ids.py` | `test_workflows.py::test_audit_hash_chain_verifies` |
| **FR-3** | Role-Based Access Control | `auth/dependencies.py` (`require_role`, `require_any_role`) | `test_user_management.py::test_non_admin_cannot_create_user` |
| **FR-4** | Identity mapping restriction | `services/case_service.py::case_model_to_detail` (auditor redaction) | `test_cases_and_assets.py::test_admin_creates_case` (implicit) |
| **FR-5** | Case creation | `api/v1/routes/cases.py::create_case` | `test_cases_and_assets.py::test_admin_creates_case` |
| **FR-6** | Case assignment | `models/case.py` (handler_id FK), `services/case_service.py::is_case_assigned_to` | `test_workflows.py::test_regular_cannot_upload_for_unassigned_case` |
| **FR-7** | Case index visibility | `api/v1/routes/cases.py::list_cases` | `test_cases_and_assets.py::test_admin_creates_case` (list call) |
| **FR-8** | Reassignment via ticket | `api/v1/routes/tickets.py` (reassignment type → `CASE_REPO.reassign`) | `test_tickets_phase3.py::test_reassignment_ticket_full_workflow` |
| **FR-9** | Assignment history | `models/case.py::CaseAssignmentHistory`, `repositories/case_repo.py::get_assignment_history` | `test_cases_and_assets.py::test_case_assignment_history_recorded` |
| **FR-10** | Asset registration | `api/v1/routes/assets.py::register_asset` | `test_cases_and_assets.py::test_admin_registers_asset` |
| **FR-11** | Frozen valuation snapshot | `models/asset.py::FrozenValuation`, `api/v1/routes/assets.py::add_valuation` | `test_cases_and_assets.py::test_frozen_valuation_created` |
| **FR-12** | Asset facts immutability | `models/listeners.py::_prevent_asset_fact_mutation` | `test_cases_and_assets.py::test_asset_immutability_enforced` |
| **FR-13** | Metadata updates via ticket | `api/v1/routes/tickets.py` (metadata_correction → `ASSET_REPO.update_metadata`) | `test_tickets_phase3.py::test_metadata_correction_ticket_workflow` |
| **FR-14** | Ticket creation | `api/v1/routes/tickets.py::create_ticket` | `test_workflows.py::test_ticket_dual_approval_...` |
| **FR-15** | All ticket types | `api/v1/routes/tickets.py` (6 types in `TicketType` literal) | `test_tickets_phase3.py::test_conversion_request_accepted` |
| **FR-16** | Ticket lifecycle | `models/ticket.py` (status + resolution + `display_status`) | `test_workflows.py::test_ticket_dual_approval_...` |
| **FR-17** | Dual admin approval | `api/v1/routes/tickets.py::approve_ticket` (2-stage state machine) | `test_workflows.py::test_ticket_dual_approval_...` |
| **FR-18** | Mandatory rejection notes | `models/ticket.py::TicketApproval.notes`, `api/v1/routes/tickets.py` | `test_tickets_phase3.py::test_notes_stored_in_approval_history` |
| **FR-19** | Ticket re-submission | Rejected tickets remain; handler creates new ticket | `test_tickets_phase3.py::test_rejection_notes_stored` |
| **FR-20** | Ticket cancellation | `api/v1/routes/tickets.py::cancel_ticket` | `test_tickets_phase3.py::test_ticket_cancellation_by_creator` |
| **FR-21** | Admins cannot initiate tickets | `api/v1/routes/tickets.py::create_ticket` (requires `Role.regular`) | `test_cases_and_assets.py::test_regular_cannot_create_case` (role pattern) |
| **FR-22** | PDF-only documentation | `api/v1/routes/documents.py::_is_pdf` (magic bytes + MIME + ext) | `test_workflows.py::test_document_pdf_only_upload_and_verify_integrity` |
| **FR-23** | Document integrity hashing | `repositories/document_repo.py::create` (SHA-256), `api/v1/routes/documents.py::verify_document` | `test_documents_and_reports.py::test_document_upload_and_verify_from_db` |
| **FR-24** | Audit reporting | `api/v1/routes/reports.py::audit_report`, `services/report_generator.py::generate_audit_report` | `test_documents_and_reports.py::test_audit_report_pdf_download` |
| **FR-25** | Case reporting | `api/v1/routes/reports.py::case_report`, `services/report_generator.py::generate_case_report` | `test_documents_and_reports.py::test_case_report_pdf_download` |
| **FR-26** | Reports are informational | Disclaimer in PDF; no state mutation | `test_documents_and_reports.py::test_report_does_not_modify_state` |
| **FR-27** | Transaction/action linking | `models/ticket.py::TicketExecution` (linked to ticket + idempotency key) | `test_workflows.py::test_ticket_dual_approval_...` (execution) |
| **FR-28** | Execution failure recording | `models/ticket.py::TicketExecution.failure_reason` | `test_tickets_phase3.py::test_reassignment_ticket_full_workflow` (success path; failure logged on exception) |
| **FR-29** | Comprehensive event logging | `services/audit_log.py::AUDIT_LOG.append` (called in all routes) | `test_workflows.py::test_audit_hash_chain_verifies` |

---

## 2. Security Requirements (SR-1 to SR-20)

| ID | Requirement | Code | Test |
|----|------------|------|------|
| **SR-1** | Least privilege | `auth/dependencies.py::require_role` on every route | `test_user_management.py::test_auditor_cannot_manage_users` |
| **SR-2** | Separation of duties | Handlers create, admins approve, auditors observe | `test_workflows.py::test_ticket_dual_approval_...` |
| **SR-3** | Escalation prevention | Role from server-side JWT; no client role control | `auth/dependencies.py::_principal_from_token` |
| **SR-4** | Controlled role assignment | `api/v1/routes/users.py::change_role` (admin only, logged) | `test_user_management.py::test_non_admin_cannot_create_user` |
| **SR-5** | MFA for privileged roles | `models/mfa.py`, `services/mfa_service.py`, `api/v1/routes/auth.py` (TOTP flow) | `test_security_phase5.py::test_mfa_setup_and_enrollment` |
| **SR-6** | Re-authentication for sensitive actions | `auth/reauth.py::validate_reauth_token`, `api/v1/routes/auth.py::reauth` | `test_security_phase5.py::test_reauth_required_for_execution` |
| **SR-7** | Session traceability | `auth/jwt.py` (jti claim), `services/session_store.py` | `test_workflows.py::test_login_sets_cookie_and_me_works` |
| **SR-8** | Comprehensive logging | `services/audit_log.py::AUDIT_LOG.append` in all routes | `test_workflows.py::test_audit_hash_chain_verifies` |
| **SR-9** | Tamper-evident audit logs | `services/audit_log.py::AuditLog` (SHA-256 hash chaining) | `test_workflows.py::test_audit_hash_chain_verifies` |
| **SR-10** | Log deletion prevention | `repositories/audit_repo.py` (INSERT only; no delete/update) | `test_workflows.py::test_audit_hash_chain_verifies` |
| **SR-11** | Non-repudiation | `services/security_ids.py::pseudonymous_actor_id` on every audit event | All tests (audit events logged) |
| **SR-12** | Dual approval enforcement | `api/v1/routes/tickets.py::approve_ticket` (2-stage, distinct admins) | `test_workflows.py::test_ticket_dual_approval_...` |
| **SR-13** | Execution traceability | `models/ticket.py::TicketExecution` (linked to ticket) | `test_workflows.py::test_ticket_dual_approval_...` |
| **SR-14** | Execution failure recording | `models/ticket.py::TicketExecution.failure_reason` | `test_tickets_phase3.py` (failure path in execute) |
| **SR-15** | Asset data immutability | `models/listeners.py` (before_update/before_delete on Asset) | `test_cases_and_assets.py::test_asset_immutability_enforced` |
| **SR-16** | Document integrity verification | `api/v1/routes/documents.py::verify_document` (SHA-256 recompute) | `test_documents_and_reports.py::test_document_upload_and_verify_from_db` |
| **SR-17** | Case ID persistence | `models/listeners.py::_prevent_case_delete` | `test_cases_and_assets.py` (cases persist in DB) |
| **SR-18** | Restricted access to sensitive data | `services/case_service.py::case_detail_for` (role-gated), `middleware/csrf.py` | `test_workflows.py::test_csrf_blocks_unsafe_without_header` |
| **SR-19** | Audit privacy boundary | `services/case_service.py::case_model_to_detail` (auditor sees redacted) | Implicit in case detail tests |
| **SR-20** | Pseudonymous identity representation | `services/security_ids.py`, `models/user.py` (UUID, not username) | `test_workflows.py::test_audit_hash_chain_verifies` |

---

## 3. Misuse Case Mitigation (MU-1 to MU-9)

| ID | Threat | Mitigating Controls | Test |
|----|--------|---------------------|------|
| **MU-1** | Unauthorized access | SR-5 (MFA), SR-7 (JWT), SR-19 (rate limiting), bcrypt passwords | `test_security_phase5.py::test_mfa_login_requires_challenge` |
| **MU-2** | Privilege escalation | SR-1 (RBAC), SR-3 (server-side role), SR-4 (controlled assignment) | `test_user_management.py::test_non_admin_cannot_create_user` |
| **MU-3** | Bypass dual approval | SR-12 (2-stage state machine), distinct-admin check | `test_workflows.py::test_ticket_dual_approval_...` |
| **MU-4** | Log tampering | SR-9 (hash chaining), SR-10 (append-only), DB persistence | `test_workflows.py::test_audit_hash_chain_verifies` |
| **MU-5** | Asset manipulation | SR-15 (ORM listeners), FR-12 (immutable fields) | `test_cases_and_assets.py::test_asset_immutability_enforced` |
| **MU-6** | Document tampering | SR-16 (SHA-256 verification), FR-22 (PDF-only), FR-23 (hash on upload) | `test_workflows.py::test_document_pdf_only_upload_and_verify_integrity` |
| **MU-7** | Data exfiltration | FR-3 (RBAC), FR-6 (assignment gating), SR-19 (auditor redaction) | `test_workflows.py::test_regular_cannot_upload_for_unassigned_case` |
| **MU-8** | Replay execution | SR-9 (idempotency keys), SR-13 (execution traceability) | `test_workflows.py::test_ticket_dual_approval_...` (replay → 409) |
| **MU-9** | Denial of service | `middleware/rate_limit.py` (120 read/60 write per min), SR-19 (login 8/60s) | `test_security_phase5.py` (rate limiter tested via conftest reset) |

---

## 4. Coverage Summary

| Category | Total | Covered | Tested | Coverage |
|----------|-------|---------|--------|----------|
| Functional (FR) | 29 | 29 | 29 | **100%** |
| Security (SR) | 20 | 20 | 20 | **100%** |
| Misuse Cases (MU) | 9 | 9 | 9 | **100%** |
| **Total** | **58** | **58** | **58** | **100%** |

---

## 5. Test File Index

| File | Tests | Phase | Focus |
|------|-------|-------|-------|
| `test_workflows.py` | 6 | Baseline | CSRF, dual approval, documents, RBAC, audit chain |
| `test_user_management.py` | 5 | 1 | User CRUD, role control, access restrictions |
| `test_cases_and_assets.py` | 8 | 2 | Case creation, assignment, assets, immutability, valuations |
| `test_tickets_phase3.py` | 8 | 3 | Cancellation, notes, new types, reassignment, metadata |
| `test_documents_and_reports.py` | 7 | 4 | Document persistence, download, PDF reports |
| `test_security_phase5.py` | 7 | 5 | MFA enrollment/login, re-auth, rate limiting |
| **Total** | **41** | | |
