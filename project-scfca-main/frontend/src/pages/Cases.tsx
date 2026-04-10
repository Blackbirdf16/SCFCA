import { useEffect, useMemo, useState } from "react";
import FormContainer from "../components/FormContainer";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { casesService, CaseDetail, CaseIndexItem } from "../services/cases";
import { documentsService } from "../services/documents";
import { ticketsService } from "../services/tickets";
import { DocumentItem, Ticket } from "../types";
import { useAuth } from "../hooks/useAuth";

export default function Cases() {
  const [cases, setCases] = useState<CaseIndexItem[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [selectedDetails, setSelectedDetails] = useState<CaseDetail | null>(null);
  const [error, setError] = useState("");
  const { user } = useAuth();

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [caseIndex, t, d] = await Promise.all([
          casesService.listIndex(),
          ticketsService.list(),
          documentsService.list()
        ]);
        if (cancelled) return;
        setCases(caseIndex);
        setTickets(t);
        setDocuments(d);
        setSelectedCaseId(caseIndex[0]?.id ?? null);
      } catch (e: any) {
        if (!cancelled) setError(e?.response?.data?.detail ?? "Failed to load cases");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const visibleCases = useMemo(() => {
    if (!user) return [];
    // Backend allows all authenticated users to view the case index.
    return cases;
  }, [cases, user]);

  useEffect(() => {
    if (!visibleCases.length) {
      setSelectedCaseId(null);
      setSelectedDetails(null);
      return;
    }
    const stillVisible = visibleCases.some((c) => c.id === selectedCaseId);
    if (!stillVisible) {
      setSelectedCaseId(visibleCases[0].id);
    }
  }, [selectedCaseId, visibleCases]);

  useEffect(() => {
    if (!selectedCaseId) {
      setSelectedDetails(null);
      return;
    }

    let cancelled = false;
    setError("");
    (async () => {
      try {
        const details = await casesService.getDetails(selectedCaseId);
        if (!cancelled) setSelectedDetails(details);
      } catch (e: any) {
        if (cancelled) return;
        setSelectedDetails(null);
        setError(e?.response?.data?.detail ?? "Not authorized to view case details");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedCaseId]);

  const linkedTickets = useMemo(() => {
    if (!selectedCaseId) return [];
    return tickets.filter((t) => t.caseId === selectedCaseId);
  }, [selectedCaseId, tickets]);

  const linkedDocuments = useMemo(() => {
    if (!selectedCaseId) return [];
    return documents.filter((d) => (d.caseId ?? "") === selectedCaseId);
  }, [documents, selectedCaseId]);

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Wallet Custody Cases">
          {error ? <div className="text-xs text-rose-300 mb-3">{error}</div> : null}
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Case ID</th>
                <th className="py-2">Custody Status</th>
              </tr>
            </thead>
            <tbody>
              {visibleCases.map((item) => (
                <tr
                  key={item.id}
                  className="border-b border-slate-800 cursor-pointer hover:bg-slate-800/40"
                  onClick={() => setSelectedCaseId(item.id)}
                >
                  <td className="py-2">{item.id}</td>
                  <td className="py-2"><StatusBadge status={item.custodyStatus} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        <FormContainer title="Case Management">
          <p className="text-sm text-slate-400">Case creation/assignment is not exposed by the hardened backend PoC API.</p>
        </FormContainer>

        <FormContainer title="Custody Case Details">
          {selectedCaseId ? (
            <div className="text-sm space-y-4 text-slate-200">
              <div className="space-y-2">
                <p><span className="text-slate-400">Case ID:</span> {selectedCaseId}</p>
                <p><span className="text-slate-400">Custody status:</span> <StatusBadge status={(selectedDetails?.custodyStatus as any) ?? "open"} /></p>
                <p><span className="text-slate-400">Wallet reference:</span> <span className="font-mono text-xs text-slate-300">{selectedDetails?.walletRef ?? "—"}</span></p>
                <p><span className="text-slate-400">Title:</span> {selectedDetails?.title ?? "—"}</p>
                <p><span className="text-slate-400">Assigned handler:</span> {selectedDetails?.handler ?? "—"}</p>
                {selectedDetails?.redacted ? (
                  <p className="text-xs text-slate-500">Details redacted for this role.</p>
                ) : null}
              </div>

              {selectedDetails?.holdings?.length ? (
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">Holdings</div>
                  <div className="space-y-2">
                    {selectedDetails.holdings.map((h, idx) => (
                      <div key={idx} className="rounded-md border border-slate-700/50 bg-dark-card/30 px-3 py-2 flex items-center justify-between">
                        <div className="text-sm font-semibold text-slate-100">{h.symbol ?? "—"}</div>
                        <div className="text-sm font-semibold tabular-nums text-slate-100">{h.balance ?? "—"}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              <div>
                <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">Linked tickets</div>
                {linkedTickets.length > 0 ? (
                  <div className="space-y-2">
                    {linkedTickets.map((t) => (
                      <div key={t.id} className="rounded-md border border-slate-700/50 bg-dark-card/30 px-3 py-2 flex items-center justify-between">
                        <div>
                          <div className="text-sm font-semibold text-slate-100">{t.ticketType.replace(/_/g, " ")}</div>
                          <div className="text-xs text-slate-400">{t.id} · Case {t.caseId}</div>
                        </div>
                        <StatusBadge status={t.status} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No tickets linked to this case.</p>
                )}
              </div>

              <div>
                <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">Linked documents</div>
                {linkedDocuments.length > 0 ? (
                  <div className="space-y-2">
                    {linkedDocuments.map((d) => (
                      <div key={d.id} className="rounded-md border border-slate-700/50 bg-dark-card/30 px-3 py-2">
                        <div className="text-sm font-semibold text-slate-100">{d.name}</div>
                        <div className="text-xs text-slate-400">{d.id} · {d.createdAt}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No documents linked to this case/wallet reference.</p>
                )}
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-400">Select a custody case to view wallet-linked details.</p>
          )}
        </FormContainer>
      </div>
    </div>
  );
}