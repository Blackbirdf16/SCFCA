import { AssetItem, CaseItem, CustodyAction, DocumentItem, Ticket, TicketStatus, TicketType, UserProfile } from "../types";
import { demoAssets, demoCases, demoCustodyActions, demoDocuments, demoTickets } from "./data";

function normalizeTicketType(value: unknown): TicketType {
  if (value === "transfer_request" || value === "custody_change" || value === "release_request") {
    return value;
  }

  const text = String(value ?? "").toLowerCase();
  if (text.includes("transfer")) return "transfer_request";
  if (text.includes("release")) return "release_request";
  return "custody_change";
}

function normalizeTicketStatus(value: unknown): TicketStatus {
  if (value === "pending_review" || value === "awaiting_second_approval" || value === "approved" || value === "rejected") {
    return value;
  }

  const text = String(value ?? "").toLowerCase();
  if (text === "pending") return "pending_review";
  if (text === "in_review") return "pending_review";
  if (text === "approved") return "approved";
  if (text === "rejected") return "rejected";
  return "pending_review";
}

function normalizeTickets(value: unknown): Ticket[] {
  if (!Array.isArray(value)) return demoTickets;

  return value
    .filter(Boolean)
    .map((raw) => {
      const item = raw as Record<string, unknown>;
      const legacyType = item.type;
      const ticketType = normalizeTicketType(item.ticketType ?? legacyType);

      const legacyDescription = typeof legacyType === "string" && legacyType ? legacyType : "";
      const description = typeof item.description === "string" && item.description.trim() ? item.description : legacyDescription;

      return {
        id: String(item.id ?? ""),
        caseId: String(item.caseId ?? ""),
        ticketType,
        description,
        status: normalizeTicketStatus(item.status),
        linkedDocumentIds: Array.isArray(item.linkedDocumentIds) ? (item.linkedDocumentIds as string[]) : [],
        approvalHistory: Array.isArray(item.approvalHistory) ? (item.approvalHistory as any) : [],
        createdBy: typeof item.createdBy === "string" ? item.createdBy : undefined,
        assignedTo: typeof item.assignedTo === "string" ? item.assignedTo : undefined
      } satisfies Ticket;
    })
    .filter((t) => Boolean(t.id) && Boolean(t.caseId));
}

function loadFromStorage<T>(key: string, fallback: T): T {
  const raw = localStorage.getItem(key);
  if (!raw) return fallback;

  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function saveToStorage<T>(key: string, value: T) {
  localStorage.setItem(key, JSON.stringify(value));
}

const KEYS = {
  cases: "scfca_poc_cases",
  assets: "scfca_poc_assets",
  tickets: "scfca_poc_tickets",
  documents: "scfca_poc_documents",
  custodyActions: "scfca_poc_custody_actions",
  profilePrefix: "scfca_poc_profile_"
} as const;

export const pocStore = {
  getCases(): CaseItem[] {
    return loadFromStorage(KEYS.cases, demoCases);
  },
  setCases(cases: CaseItem[]) {
    saveToStorage(KEYS.cases, cases);
  },

  getAssets(): AssetItem[] {
    return loadFromStorage(KEYS.assets, demoAssets);
  },
  setAssets(assets: AssetItem[]) {
    saveToStorage(KEYS.assets, assets);
  },

  getTickets(): Ticket[] {
    const raw = loadFromStorage(KEYS.tickets, demoTickets);
    return normalizeTickets(raw);
  },
  setTickets(tickets: Ticket[]) {
    saveToStorage(KEYS.tickets, tickets);
  },

  getDocuments(): DocumentItem[] {
    return loadFromStorage(KEYS.documents, demoDocuments);
  },
  setDocuments(documents: DocumentItem[]) {
    saveToStorage(KEYS.documents, documents);
  },

  getProfile(username: string): UserProfile {
    const key = `${KEYS.profilePrefix}${(username || "").trim().toLowerCase()}`;
    return loadFromStorage<UserProfile>(key, { fullName: "", nickname: "" });
  },
  setProfile(username: string, profile: UserProfile) {
    const key = `${KEYS.profilePrefix}${(username || "").trim().toLowerCase()}`;
    saveToStorage(key, profile);
  },

  getCustodyActions(): CustodyAction[] {
    return loadFromStorage(KEYS.custodyActions, demoCustodyActions);
  },
  setCustodyActions(actions: CustodyAction[]) {
    saveToStorage(KEYS.custodyActions, actions);
  }
};
