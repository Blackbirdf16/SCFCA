/**
 * Dashboard data service for SCFCA.
 *
 * Fetches real data from backend APIs. Falls back to defaults on error.
 */

import { http } from "./http";
import { AuditEvent, DashboardSummary, Ticket } from "../types";

const emptySummary: DashboardSummary = {
  totalCases: 0,
  registeredAssets: 0,
  pendingTickets: 0,
  approvedTickets: 0,
};

export const dashboardService = {
  async getDashboardData(): Promise<{
    summary: DashboardSummary;
    audit: AuditEvent[];
    tickets: Ticket[];
  }> {
    let summary = { ...emptySummary };
    let audit: AuditEvent[] = [];
    let tickets: Ticket[] = [];

    // Fetch cases count
    try {
      const casesResp = await http.get("/api/v1/cases/");
      const cases = Array.isArray(casesResp.data?.cases) ? casesResp.data.cases : [];
      summary.totalCases = cases.length;
    } catch { /* keep default */ }

    // Fetch assets count
    try {
      const assetsResp = await http.get("/api/v1/assets/");
      const assets = Array.isArray(assetsResp.data?.assets) ? assetsResp.data.assets : [];
      summary.registeredAssets = assets.length;
    } catch { /* keep default */ }

    // Fetch tickets
    try {
      const ticketsResp = await http.get("/api/v1/tickets/");
      const allTickets = Array.isArray(ticketsResp.data?.tickets) ? ticketsResp.data.tickets : [];
      tickets = allTickets.slice(0, 10);
      summary.pendingTickets = allTickets.filter(
        (t: Ticket) => t.status === "pending_review" || t.status === "awaiting_second_approval"
      ).length;
      summary.approvedTickets = allTickets.filter((t: Ticket) => t.status === "approved").length;
    } catch { /* keep default */ }

    // Fetch recent audit events
    try {
      const auditResp = await http.get("/api/v1/audit/");
      const events = Array.isArray(auditResp.data?.events) ? auditResp.data.events : [];
      audit = events.slice(0, 10).map((e: any) => ({
        id: e.id,
        timestamp: e.timestamp,
        actor: e.actorId || e.actor_id || "",
        action: e.action,
      }));
    } catch { /* keep default */ }

    return { summary, audit, tickets };
  },
};
