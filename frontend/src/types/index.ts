export type Role = "case_handler" | "administrator" | "auditor";

export interface User {
  username: string;
  role: Role;
  token?: string;
}

export type TicketStatus = "pending" | "approved" | "rejected";
export type AssetStatus = "active" | "pending" | "inactive";

export interface CaseItem {
  id: string;
  title: string;
  owner: string;
  status: "open" | "in_review" | "closed";
}

export interface AssetItem {
  id: string;
  symbol: string;
  network: string;
  status: AssetStatus;
}

export interface Ticket {
  id: string;
  caseId: string;
  type: string;
  status: TicketStatus;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
}

export interface DocumentItem {
  id: string;
  name: string;
  hash: string;
  createdAt: string;
}

export interface DashboardSummary {
  totalCases: number;
  registeredAssets: number;
  pendingTickets: number;
  approvedTickets: number;
}