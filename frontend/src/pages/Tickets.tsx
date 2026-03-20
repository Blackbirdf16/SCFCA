import { useEffect, useMemo, useState } from "react";
import FormContainer from "../components/FormContainer";
import RoleGuard from "../components/RoleGuard";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { useAuth } from "../hooks/useAuth";
import { pocStore } from "../services/pocStore";
import { DocumentItem, Ticket, TicketApprovalEvent, TicketStatus, TicketType } from "../types";
import { canApproveTickets, canCreateTickets, isReadOnlyRole } from "../utils/roles";

const TICKET_TYPE_LABELS: Record<TicketType, string> = {
  transfer_request: "Transfer request",
  custody_change: "Custody change",
  release_request: "Release request"
};

function nowTimestamp(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>(() => pocStore.getTickets());
  const [caseId, setCaseId] = useState("");
  const [ticketType, setTicketType] = useState<TicketType | "">("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const [assignTicketId, setAssignTicketId] = useState("");
  const [assignTo, setAssignTo] = useState("");
  const { user } = useAuth();

  useEffect(() => {
    pocStore.setTickets(tickets);
  }, [tickets]);

  const canApprove = user ? canApproveTickets(user.role) : false;
  const canCreate = user ? canCreateTickets(user.role) : false;
  const readOnly = user ? isReadOnlyRole(user.role) : true;

  const assignedCaseIds = useMemo(() => {
    if (!user) return new Set<string>();
    const items = pocStore.getCases();
    return new Set(items.filter((c) => c.handler === user.username).map((c) => c.id));
  }, [user]);

  const visibleTickets = useMemo(() => {
    if (!user) return [];
    if (user.role === "regular") {
      return tickets.filter((t) => (t.createdBy ?? "") === user.username && assignedCaseIds.has(t.caseId));
    }
    return tickets;
  }, [assignedCaseIds, tickets, user]);

  const cases = useMemo(() => pocStore.getCases(), []);
  const documents = useMemo(() => pocStore.getDocuments(), []);

  const ticketRows = useMemo(() => {
    const caseById = new Map(cases.map((c) => [c.id, c] as const));
    const docsById = new Map(documents.map((d) => [d.id, d] as const));

    return visibleTickets.map((ticket) => {
      const relatedCase = caseById.get(ticket.caseId);
      const walletRef = relatedCase?.walletRef;

      const explicitDocIds = Array.isArray(ticket.linkedDocumentIds) ? ticket.linkedDocumentIds : [];
      const linkedDocs = explicitDocIds.length
        ? explicitDocIds
            .map((id) => docsById.get(id))
            .filter((d): d is DocumentItem => Boolean(d))
        : documents.filter((d) => (d.caseId ?? "") === ticket.caseId);

      const approvalHistory = Array.isArray(ticket.approvalHistory) ? ticket.approvalHistory : [];
      const approvals = approvalHistory.filter((e) => e.decision === "approved");

      return {
        ticket,
        relatedCase,
        walletRef,
        linkedDocs,
        approvalHistory,
        approvals
      };
    });
  }, [cases, documents, visibleTickets]);

  const createTicket = (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    if (!user) return;
    if (readOnly || !canCreate) {
      setError("Your role is read-only and cannot create tickets.");
      return;
    }
    if (!caseId || !ticketType || !description.trim()) return;

    const normalizedCaseId = caseId.trim().toUpperCase();
    const relatedCase = pocStore.getCases().find((c) => c.id === normalizedCaseId);
    if (!relatedCase) {
      setError("Unknown custody case ID. Tickets must be linked to an existing case.");
      return;
    }
    if (user.role === "regular" && !assignedCaseIds.has(normalizedCaseId)) {
      setError("Regular users can only open tickets for assigned custody cases.");
      return;
    }

    const next: Ticket = {
      id: `T-${Math.floor(Math.random() * 900 + 100)}`,
      caseId: normalizedCaseId,
      ticketType,
      description: description.trim(),
      status: "pending_review",
      linkedDocumentIds: [],
      approvalHistory: [],
      createdBy: user.username,
      assignedTo: user.role === "administrator" ? user.username : "admin_team"
    };
    setTickets((prev) => [next, ...prev]);
    setCaseId("");
    setTicketType("");
    setDescription("");
  };

  const approveTicket = (id: string) => {
    setError("");
    if (!user) return;
    if (!canApprove) return;

    setTickets((prev) =>
      prev.map((ticket) => {
        if (ticket.id !== id) return ticket;
        if (ticket.status === "approved" || ticket.status === "rejected") return ticket;

        const approvalHistory = Array.isArray(ticket.approvalHistory) ? ticket.approvalHistory : [];
        const approvals = approvalHistory.filter((e) => e.decision === "approved");
        if (approvals.length >= 2) return ticket;

        if (approvals.some((e) => e.decidedBy === user.username)) {
          setError("This administrator has already approved this ticket.");
          return ticket;
        }

        const stage = (approvals.length + 1) as 1 | 2;
        const nextEvent: TicketApprovalEvent = {
          stage,
          decision: "approved",
          decidedBy: user.username,
          decidedAt: nowTimestamp()
        };

        const nextApprovalHistory = [nextEvent, ...approvalHistory];
        const nextStatus: TicketStatus = stage === 1 ? "awaiting_second_approval" : "approved";
        return { ...ticket, status: nextStatus, approvalHistory: nextApprovalHistory };
      })
    );
  };

  const rejectTicket = (id: string) => {
    setError("");
    if (!user) return;
    if (!canApprove) return;

    setTickets((prev) =>
      prev.map((ticket) => {
        if (ticket.id !== id) return ticket;
        if (ticket.status === "approved" || ticket.status === "rejected") return ticket;

        const approvalHistory = Array.isArray(ticket.approvalHistory) ? ticket.approvalHistory : [];
        const approvals = approvalHistory.filter((e) => e.decision === "approved");
        if (approvalHistory.some((e) => e.decidedBy === user.username && e.decision === "rejected")) {
          setError("This ticket was already rejected by this administrator.");
          return ticket;
        }

        const stage = (approvals.length >= 1 ? 2 : 1) as 1 | 2;
        const nextEvent: TicketApprovalEvent = {
          stage,
          decision: "rejected",
          decidedBy: user.username,
          decidedAt: nowTimestamp()
        };

        return { ...ticket, status: "rejected", approvalHistory: [nextEvent, ...approvalHistory] };
      })
    );
  };

  const assignTicket = (event: React.FormEvent) => {
    event.preventDefault();
    if (!canApprove) return;
    if (!assignTicketId || !assignTo) return;
    setTickets((prev) =>
      prev.map((ticket) => (ticket.id === assignTicketId ? { ...ticket, assignedTo: assignTo } : ticket))
    );
    setAssignTicketId("");
    setAssignTo("");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Ticket List">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400 border-b border-slate-700">
                  <th className="py-2">Ticket ID</th>
                  <th className="py-2">Case ID</th>
                  <th className="py-2">Wallet Ref</th>
                  <th className="py-2">Ticket Type</th>
                  <th className="py-2">Description</th>
                  <th className="py-2">Linked Docs</th>
                  <th className="py-2">Creator</th>
                  <th className="py-2">Current Status</th>
                  <th className="py-2">Approval History</th>
                  <th className="py-2">Assigned</th>
                  <th className="py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {ticketRows.map(({ ticket, walletRef, linkedDocs, approvalHistory, approvals }) => (
                  <tr key={ticket.id} className="border-b border-slate-800 align-top">
                    <td className="py-2 whitespace-nowrap">{ticket.id}</td>
                    <td className="py-2 whitespace-nowrap">{ticket.caseId}</td>
                    <td className="py-2 font-mono text-xs text-slate-300 whitespace-nowrap">{walletRef ?? "—"}</td>
                    <td className="py-2 whitespace-nowrap">{TICKET_TYPE_LABELS[ticket.ticketType]}</td>
                    <td className="py-2 text-slate-200 max-w-[360px]">
                      <div className="truncate" title={ticket.description}>{ticket.description}</div>
                    </td>
                    <td className="py-2">
                      {linkedDocs.length ? (
                        <div className="text-xs text-slate-300 space-y-1">
                          {linkedDocs.slice(0, 2).map((d) => (
                            <div key={d.id} className="font-mono">{d.id} <span className="text-slate-500">({d.name})</span></div>
                          ))}
                          {linkedDocs.length > 2 ? (
                            <div className="text-slate-500">+{linkedDocs.length - 2} more</div>
                          ) : null}
                        </div>
                      ) : (
                        <span className="text-xs text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-2 text-slate-300 whitespace-nowrap">{ticket.createdBy ?? "—"}</td>
                    <td className="py-2">
                      <div className="space-y-1">
                        <StatusBadge status={ticket.status} />
                        <div className="text-xs text-slate-500">Approvals: {approvals.length}/2</div>
                        {ticket.status === "awaiting_second_approval" ? (
                          <div className="text-xs text-slate-500">First approval complete</div>
                        ) : null}
                      </div>
                    </td>
                    <td className="py-2">
                      {approvalHistory.length ? (
                        <div className="text-xs text-slate-300 space-y-1">
                          {approvalHistory
                            .slice(0, 3)
                            .map((e, idx) => (
                              <div key={`${ticket.id}-${idx}`}>
                                <span className="text-slate-500">S{e.stage}</span> {e.decision} by <span className="font-mono">{e.decidedBy}</span>
                                <span className="text-slate-500"> @ {e.decidedAt}</span>
                              </div>
                            ))}
                        </div>
                      ) : (
                        <span className="text-xs text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-2 text-slate-300 whitespace-nowrap">{ticket.assignedTo ?? "—"}</td>
                    <td className="py-2 whitespace-nowrap">
                      {canApprove ? (
                        <div className="flex gap-2">
                          <button
                            type="button"
                            className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-300 disabled:opacity-40"
                            onClick={() => approveTicket(ticket.id)}
                            disabled={ticket.status === "approved" || ticket.status === "rejected"}
                          >
                            {approvals.length === 0 ? "Approve 1" : "Approve 2"}
                          </button>
                          <button
                            type="button"
                            className="px-2 py-1 rounded bg-rose-500/20 text-rose-300 disabled:opacity-40"
                            onClick={() => rejectTicket(ticket.id)}
                            disabled={ticket.status === "approved" || ticket.status === "rejected"}
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-500">Read-only</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        {user && canCreate && !readOnly ? (
          <FormContainer title="Create Ticket">
            <form className="space-y-3" onSubmit={createTicket}>
              <input
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder={user.role === "regular" ? "Assigned case ID" : "Case ID"}
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <select
                value={ticketType}
                onChange={(e) => setTicketType(e.target.value as TicketType)}
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              >
                <option value="" disabled>Select ticket type</option>
                <option value="transfer_request">Transfer request</option>
                <option value="custody_change">Custody change</option>
                <option value="release_request">Release request</option>
              </select>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description (what action is requested, what assets/scope, why)"
                rows={4}
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              {error ? <p className="text-xs text-rose-300">{error}</p> : null}
              <button className="accent-button w-full py-2" type="submit">Create</button>
              {user.role === "regular" ? (
                <p className="text-xs text-slate-500">Regular users can only open tickets for assigned custody cases.</p>
              ) : null}
            </form>
          </FormContainer>
        ) : (
          <FormContainer title="Create Ticket">
            <p className="text-sm text-slate-400">Ticket creation is restricted for this role.</p>
          </FormContainer>
        )}

        <RoleGuard
          allow={["administrator"]}
          fallback={
            <FormContainer title="Approval Workflow">
              <p className="text-sm text-slate-400">Only administrators can approve/reject or assign tickets.</p>
            </FormContainer>
          }
        >
          <FormContainer title="Approval Workflow">
            <p className="text-sm text-slate-300">Custody tickets require two distinct administrator approvals before final approval.</p>
            <div className="mt-2 text-xs text-slate-500 space-y-1">
              <div><span className="font-semibold">pending review</span>: no approvals recorded</div>
              <div><span className="font-semibold">awaiting second approval</span>: first approval complete</div>
              <div><span className="font-semibold">approved</span>: second approval recorded</div>
              <div><span className="font-semibold">rejected</span>: rejected at any stage</div>
            </div>
          </FormContainer>

          <FormContainer title="Assign Ticket (PoC)">
            <form className="space-y-3" onSubmit={assignTicket}>
              <input
                value={assignTicketId}
                onChange={(e) => setAssignTicketId(e.target.value)}
                placeholder="Ticket ID (e.g. T-201)"
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <input
                value={assignTo}
                onChange={(e) => setAssignTo(e.target.value)}
                placeholder="Assign to (operator/team)"
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <button className="accent-button w-full py-2" type="submit">Assign</button>
            </form>
          </FormContainer>
        </RoleGuard>
      </div>
    </div>
  );
}