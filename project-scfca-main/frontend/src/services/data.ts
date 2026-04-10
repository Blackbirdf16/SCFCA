import { AssetItem, AuditEvent, CaseItem, CustodyAction, DocumentItem, Ticket } from "../types";

export const demoCases: CaseItem[] = [
  {
    id: "C-100",
    walletRef: "WLT-8F3A-PRIMARY",
    title: "Corporate cold wallet rotation",
    handler: "ops_team",
    custodyStatus: "open",
    holdings: [
      { symbol: "BTC", balance: 12.5 },
      { symbol: "ETH", balance: 180 }
    ]
  },
  {
    id: "C-101",
    walletRef: "WLT-21C9-MSIG",
    title: "Multi-sig governance update",
    handler: "admin_team",
    custodyStatus: "in_review",
    holdings: [
      { symbol: "BTC", balance: 2 },
      { symbol: "USDC", balance: 500000 }
    ]
  }
];

export const demoAssets: AssetItem[] = [
  {
    id: "AS-01",
    symbol: "BTC",
    assetType: "coin",
    balance: 12.5,
    protocol: "Native",
    network: "Bitcoin",
    walletRef: "WLT-8F3A-PRIMARY",
    caseId: "C-100",
    status: "active"
  },
  {
    id: "AS-02",
    symbol: "ETH",
    assetType: "coin",
    balance: 180,
    protocol: "Native",
    network: "Ethereum",
    walletRef: "WLT-8F3A-PRIMARY",
    caseId: "C-100",
    status: "active"
  },
  {
    id: "AS-03",
    symbol: "USDC",
    assetType: "stablecoin",
    balance: 500000,
    protocol: "ERC-20",
    network: "Ethereum",
    walletRef: "WLT-21C9-MSIG",
    caseId: "C-101",
    status: "pending"
  }
];

export const demoCustodyActions: CustodyAction[] = [
  {
    id: "ACT-300",
    createdAt: "2026-03-19 11:20",
    type: "transfer_request",
    status: "requested",
    requestedBy: "ops_team",
    walletRef: "WLT-8F3A-PRIMARY",
    symbol: "BTC",
    amount: 0.75,
    network: "Bitcoin",
    protocol: "Native",
    destination: "bc1q...demo_destination",
    caseId: "C-100",
    notes: "PoC transfer request (no signing/execution)"
  },
  {
    id: "ACT-301",
    createdAt: "2026-03-19 14:05",
    type: "custody_movement",
    status: "in_review",
    requestedBy: "admin_team",
    walletRef: "WLT-21C9-MSIG",
    symbol: "USDC",
    amount: 250000,
    network: "Ethereum",
    protocol: "ERC-20",
    caseId: "C-101",
    notes: "PoC custody movement request (internal re-allocation)"
  }
];

export const demoTickets: Ticket[] = [
  {
    id: "T-201",
    caseId: "C-100",
    ticketType: "transfer_request",
    description: "Transfer 0.75 BTC to pre-approved destination (PoC request).",
    status: "awaiting_second_approval",
    linkedDocumentIds: ["DOC-77"],
    approvalHistory: [
      {
        stage: 1,
        decision: "approved",
        decidedBy: "admin01",
        decidedAt: "2026-03-19 12:10"
      }
    ],
    createdBy: "ops_team",
    assignedTo: "admin_team"
  },
  {
    id: "T-202",
    caseId: "C-101",
    ticketType: "custody_change",
    description: "Update multi-sig approver set (PoC custody change).",
    status: "approved",
    linkedDocumentIds: ["DOC-78"],
    approvalHistory: [
      {
        stage: 1,
        decision: "approved",
        decidedBy: "admin01",
        decidedAt: "2026-03-19 09:40"
      },
      {
        stage: 2,
        decision: "approved",
        decidedBy: "admin02",
        decidedAt: "2026-03-19 10:05"
      }
    ],
    createdBy: "admin_team",
    assignedTo: "admin_team"
  },
  {
    id: "T-203",
    caseId: "C-100",
    ticketType: "release_request",
    description: "Release assets from custody case upon completion (PoC).",
    status: "pending_review",
    linkedDocumentIds: [],
    approvalHistory: [],
    createdBy: "ops_team",
    assignedTo: "admin_team"
  }
];

export const demoAudit: AuditEvent[] = [
  { id: "AU-001", timestamp: "2026-03-19 10:05", actor: "auditor01", action: "Checked signature chain" },
  { id: "AU-002", timestamp: "2026-03-19 10:25", actor: "admin01", action: "Updated ticket policy" }
];

export const demoDocuments: DocumentItem[] = [
  {
    id: "DOC-77",
    name: "custody_policy_v2.pdf",
    hash: "sha256:AA1BB2CC3",
    createdAt: "2026-03-18",
    caseId: "C-100",
    walletRef: "WLT-8F3A-PRIMARY",
    uploadedBy: "ops_team"
  },
  {
    id: "DOC-78",
    name: "audit_trace_Q1.csv",
    hash: "sha256:DD4EE5FF6",
    createdAt: "2026-03-19",
    caseId: "C-101",
    walletRef: "WLT-21C9-MSIG",
    uploadedBy: "admin_team"
  }
];