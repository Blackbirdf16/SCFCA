import { http } from "./http";
import { AuditEvent, DashboardSummary, Ticket } from "../types";

const fallbackSummary: DashboardSummary = {
  totalCases: 12,
  registeredAssets: 28,
  pendingTickets: 4,
  approvedTickets: 19
};

const fallbackAudit: AuditEvent[] = [
  { id: "A-001", timestamp: "2026-03-19 09:30", actor: "admin01", action: "Approved transfer request" },
  { id: "A-002", timestamp: "2026-03-19 08:10", actor: "auditor01", action: "Reviewed ticket trail" }
];

const fallbackTickets: Ticket[] = [
  { id: "T-109", caseId: "C-334", type: "Withdrawal", status: "pending" },
  { id: "T-107", caseId: "C-332", type: "Policy change", status: "approved" }
];

export const dashboardService = {
  async getDashboardData(): Promise<{ summary: DashboardSummary; audit: AuditEvent[]; tickets: Ticket[] }> {
    let summary = fallbackSummary;
    let casesCount = 0;

    try {
      const casesResponse = await http.get("/api/v1/cases/");
      const cases = Array.isArray(casesResponse.data?.cases) ? casesResponse.data.cases : [];
      casesCount = cases.length;
      summary = {
        ...fallbackSummary,
        totalCases: casesCount
      };
    } catch {
      summary = fallbackSummary;
    }

    return {
      summary,
      audit: fallbackAudit,
      tickets: fallbackTickets
    };
  }
};