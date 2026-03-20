import { AssetItem, AuditEvent, CaseItem, DocumentItem, Ticket } from "../types";

export const demoCases: CaseItem[] = [
  { id: "C-100", title: "Corporate Cold Wallet Rotation", owner: "ops_team", status: "open" },
  { id: "C-101", title: "Multi-sig Governance Update", owner: "admin_team", status: "in_review" }
];

export const demoAssets: AssetItem[] = [
  { id: "AS-01", symbol: "BTC", network: "Bitcoin", status: "active" },
  { id: "AS-02", symbol: "ETH", network: "Ethereum", status: "pending" }
];

export const demoTickets: Ticket[] = [
  { id: "T-201", caseId: "C-100", type: "Transfer approval", status: "pending" },
  { id: "T-202", caseId: "C-101", type: "Access update", status: "approved" }
];

export const demoAudit: AuditEvent[] = [
  { id: "AU-001", timestamp: "2026-03-19 10:05", actor: "auditor01", action: "Checked signature chain" },
  { id: "AU-002", timestamp: "2026-03-19 10:25", actor: "admin01", action: "Updated ticket policy" }
];

export const demoDocuments: DocumentItem[] = [
  { id: "DOC-77", name: "custody_policy_v2.pdf", hash: "sha256:AA1BB2CC3", createdAt: "2026-03-18" },
  { id: "DOC-78", name: "audit_trace_Q1.csv", hash: "sha256:DD4EE5FF6", createdAt: "2026-03-19" }
];