import { useState } from "react";
import FormContainer from "../components/FormContainer";
import RoleGuard from "../components/RoleGuard";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { useAuth } from "../hooks/useAuth";
import { demoTickets } from "../services/data";
import { Ticket, TicketStatus } from "../types";
import { canApproveTickets } from "../utils/roles";

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>(demoTickets);
  const [caseId, setCaseId] = useState("");
  const [type, setType] = useState("");
  const { user } = useAuth();

  const canApprove = user ? canApproveTickets(user.role) : false;

  const createTicket = (event: React.FormEvent) => {
    event.preventDefault();
    if (!caseId || !type) return;

    const next: Ticket = {
      id: `T-${Math.floor(Math.random() * 900 + 100)}`,
      caseId,
      type,
      status: "pending"
    };
    setTickets((prev) => [next, ...prev]);
    setCaseId("");
    setType("");
  };

  const updateStatus = (id: string, status: TicketStatus) => {
    setTickets((prev) => prev.map((ticket) => (ticket.id === id ? { ...ticket, status } : ticket)));
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Ticket List">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Ticket ID</th>
                <th className="py-2">Case</th>
                <th className="py-2">Type</th>
                <th className="py-2">Status</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((ticket) => (
                <tr key={ticket.id} className="border-b border-slate-800">
                  <td className="py-2">{ticket.id}</td>
                  <td className="py-2">{ticket.caseId}</td>
                  <td className="py-2">{ticket.type}</td>
                  <td className="py-2"><StatusBadge status={ticket.status} /></td>
                  <td className="py-2">
                    {canApprove ? (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-300"
                          onClick={() => updateStatus(ticket.id, "approved")}
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          className="px-2 py-1 rounded bg-rose-500/20 text-rose-300"
                          onClick={() => updateStatus(ticket.id, "rejected")}
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">Restricted</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        <FormContainer title="Create Ticket">
          <form className="space-y-3" onSubmit={createTicket}>
            <input
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              placeholder="Case ID"
              className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
            />
            <input
              value={type}
              onChange={(e) => setType(e.target.value)}
              placeholder="Ticket type"
              className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
            />
            <button className="accent-button w-full py-2" type="submit">Create</button>
          </form>
        </FormContainer>

        <RoleGuard
          allow={["administrator"]}
          fallback={
            <FormContainer title="Approval Workflow">
              <p className="text-sm text-slate-400">Only administrators can approve or reject tickets.</p>
            </FormContainer>
          }
        >
          <FormContainer title="Approval Workflow">
            <p className="text-sm text-slate-300">Use action buttons in the ticket table to approve or reject pending requests.</p>
          </FormContainer>
        </RoleGuard>
      </div>
    </div>
  );
}