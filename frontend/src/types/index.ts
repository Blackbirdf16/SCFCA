export type Role = "regular" | "administrator" | "auditor";

export interface User {
  username: string;
  role: Role;
  token?: string;
}

export interface UserProfile {
  fullName: string;
  nickname: string;
}

export type TicketType = "transfer_request" | "custody_change" | "release_request";

export type TicketStatus = "pending_review" | "awaiting_second_approval" | "approved" | "rejected";

export type TicketApprovalDecision = "approved" | "rejected";

export interface TicketApprovalEvent {
  stage: 1 | 2;
  decision: TicketApprovalDecision;
  decidedBy: string;
  decidedAt: string;
}
export type AssetStatus = "active" | "pending" | "inactive";

export type CustodyActionType = "transfer_request" | "custody_movement" | "release_request";
export type CustodyActionStatus = "requested" | "in_review" | "approved" | "rejected" | "executed" | "cancelled";
export type AssetType = "coin" | "stablecoin" | "token" | "other";

export interface CaseItem {
  id: string;
  walletRef: string;
  title: string;
  handler: string;
  custodyStatus: "open" | "in_review" | "closed";
  holdings: Holding[];
}

export interface Holding {
  symbol: string;
  balance: number;
}

export interface AssetItem {
  id: string;
  symbol: string;
  network: string;
  status: AssetStatus;
  walletRef?: string;
  balance?: number;
  assetType?: AssetType;
  protocol?: string;
  caseId?: string;
}

export interface CustodyAction {
  id: string;
  createdAt: string;
  type: CustodyActionType;
  status: CustodyActionStatus;
  requestedBy?: string;
  walletRef: string;
  symbol: string;
  amount: number;
  network?: string;
  protocol?: string;
  destination?: string;
  caseId?: string;
  notes?: string;
}

export interface Ticket {
  id: string;
  caseId: string;
  ticketType: TicketType;
  description: string;
  status: TicketStatus;
  linkedDocumentIds?: string[];
  approvalHistory?: TicketApprovalEvent[];
  createdBy?: string;
  assignedTo?: string;
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
  caseId?: string;
  walletRef?: string;
  uploadedBy?: string;
}

export interface DashboardSummary {
  totalCases: number;
  registeredAssets: number;
  pendingTickets: number;
  approvedTickets: number;
}