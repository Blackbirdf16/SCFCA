import { useEffect, useState } from "react";
import KpiCard from "../components/KpiCard";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { dashboardService } from "../services/dashboard";
import { useAuth } from "../hooks/useAuth";
import { AuditEvent, DashboardSummary, Ticket } from "../types";

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary>({
    totalCases: 0,
    registeredAssets: 0,
    pendingTickets: 0,
    approvedTickets: 0
  });
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const { user } = useAuth();

  useEffect(() => {
    const load = async () => {
      const data = await dashboardService.getDashboardData();
      setSummary(data.summary);
      setAuditEvents(data.audit);
      setTickets(data.tickets);
    };
    void load();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold text-gold mb-8">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4 mb-8">
        <KpiCard title="Total Cases" value={summary.totalCases} />
        <KpiCard title="Registered Assets" value={summary.registeredAssets} />
        <KpiCard title="Pending Tickets" value={summary.pendingTickets} />
        <KpiCard title="Approved Tickets" value={summary.approvedTickets} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <TableWrapper title="Recent Audit Events">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Timestamp</th>
                <th className="py-2">Actor</th>
                <th className="py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {auditEvents.map((event) => (
                <tr key={event.id} className="border-b border-slate-800">
                  <td className="py-2">{event.timestamp}</td>
                  <td className="py-2">{event.actor}</td>
                  <td className="py-2">{event.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>

        <TableWrapper title="Recent Tickets">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Ticket ID</th>
                <th className="py-2">Case</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((ticket) => (
                <tr key={ticket.id} className="border-b border-slate-800">
                  <td className="py-2">{ticket.id}</td>
                  <td className="py-2">{ticket.caseId}</td>
                  <td className="py-2"><StatusBadge status={ticket.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="mt-6 rounded-xl border border-slate-700/60 bg-dark-panel p-5">
        <h3 className="text-gold font-semibold mb-2">User Summary</h3>
        <p className="text-sm text-slate-300">Username: {user?.username ?? "demo"}</p>
        <p className="text-sm text-slate-300">Role: {user?.role ?? "unknown"}</p>
      </div>
    </div>
  );
}
