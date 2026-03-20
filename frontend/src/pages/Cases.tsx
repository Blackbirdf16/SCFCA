import { useEffect, useMemo, useState } from "react";
import FormContainer from "../components/FormContainer";
import RoleGuard from "../components/RoleGuard";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { CaseItem } from "../types";
import { pocStore } from "../services/pocStore";
import { useAuth } from "../hooks/useAuth";

export default function Cases() {
  const [cases, setCases] = useState<CaseItem[]>(() => pocStore.getCases());
  const [title, setTitle] = useState("");
  const [handler, setHandler] = useState("");
  const [walletRef, setWalletRef] = useState("");
  const { user } = useAuth();
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(() => pocStore.getCases()[0]?.id ?? null);

  useEffect(() => {
    pocStore.setCases(cases);
  }, [cases]);

  const visibleCases = useMemo(() => {
    if (!user) return [];
    if (user.role === "regular") {
      return cases.filter((c) => c.handler === user.username);
    }
    return cases;
  }, [cases, user]);

  useEffect(() => {
    if (!visibleCases.length) {
      setSelectedCaseId(null);
      return;
    }
    const stillVisible = visibleCases.some((c) => c.id === selectedCaseId);
    if (!stillVisible) {
      setSelectedCaseId(visibleCases[0].id);
    }
  }, [selectedCaseId, visibleCases]);

  const selected = useMemo(
    () => visibleCases.find((item) => item.id === selectedCaseId) ?? null,
    [visibleCases, selectedCaseId]
  );

  const onCreateCase = (event: React.FormEvent) => {
    event.preventDefault();
    if (!title || !handler || !walletRef) return;

    const newCase: CaseItem = {
      id: `C-${Math.floor(Math.random() * 900 + 100)}`,
      walletRef,
      title,
      handler,
      custodyStatus: "open",
      holdings: []
    };
    setCases((prev) => [newCase, ...prev]);
    setTitle("");
    setHandler("");
    setWalletRef("");
    setSelectedCaseId(newCase.id);
  };

  const assets = useMemo(() => pocStore.getAssets(), []);
  const tickets = useMemo(() => pocStore.getTickets(), []);
  const documents = useMemo(() => pocStore.getDocuments(), []);

  const visibleTickets = useMemo(() => {
    if (!user) return [];
    if (user.role === "regular") {
      return tickets.filter((t) => (t.createdBy ?? "") === user.username);
    }
    return tickets;
  }, [tickets, user]);

  const visibleDocuments = useMemo(() => {
    if (!user) return [];
    if (user.role === "regular") {
      return documents.filter((d) => (d.uploadedBy ?? "") === user.username);
    }
    return documents;
  }, [documents, user]);

  const linkedAssets = useMemo(() => {
    if (!selected) return [];
    return assets.filter((a) => a.walletRef && a.walletRef === selected.walletRef);
  }, [assets, selected]);

  const linkedTickets = useMemo(() => {
    if (!selected) return [];
    return visibleTickets.filter((t) => t.caseId === selected.id);
  }, [visibleTickets, selected]);

  const linkedDocuments = useMemo(() => {
    if (!selected) return [];
    return visibleDocuments.filter(
      (d) => (d.caseId && d.caseId === selected.id) || (d.walletRef && d.walletRef === selected.walletRef)
    );
  }, [visibleDocuments, selected]);

  const coinsSummary = (item: CaseItem) => {
    const symbols = (item.holdings ?? []).map((h) => h.symbol);
    if (symbols.length > 0) return symbols.join(", ");

    const symbolsFromRegistry = assets
      .filter((a) => a.walletRef && a.walletRef === item.walletRef)
      .map((a) => a.symbol);
    if (symbolsFromRegistry.length > 0) return Array.from(new Set(symbolsFromRegistry)).join(", ");

    return "—";
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Wallet Custody Cases">
          {user?.role === "regular" ? (
            <div className="text-xs text-slate-400 mb-3">
              Scoped view: showing only custody cases assigned to <span className="text-slate-200 font-semibold">{user.username}</span>.
            </div>
          ) : null}
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Case ID</th>
                <th className="py-2">Wallet Ref</th>
                <th className="py-2">Title</th>
                <th className="py-2">Handler</th>
                <th className="py-2">Custody Status</th>
                <th className="py-2">Coins</th>
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
                  <td className="py-2 font-mono text-xs text-slate-300">{item.walletRef}</td>
                  <td className="py-2">{item.title}</td>
                  <td className="py-2">{item.handler}</td>
                  <td className="py-2"><StatusBadge status={item.custodyStatus} /></td>
                  <td className="py-2 text-slate-300">{coinsSummary(item)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        <RoleGuard
          allow={["administrator"]}
          fallback={
            <FormContainer title="Case Management">
              <p className="text-sm text-slate-400">Only administrators can create or assign custody cases in this PoC.</p>
            </FormContainer>
          }
        >
          <FormContainer title="Create Wallet Custody Case">
            <form className="space-y-3" onSubmit={onCreateCase}>
              <input
                value={walletRef}
                onChange={(e) => setWalletRef(e.target.value.toUpperCase())}
                placeholder="Wallet reference (e.g. WLT-XXXX)"
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Custody case title"
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <input
                value={handler}
                onChange={(e) => setHandler(e.target.value)}
                placeholder="Assigned handler / responsible account"
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <button className="accent-button w-full py-2" type="submit">Create</button>
            </form>
          </FormContainer>
        </RoleGuard>

        <FormContainer title="Custody Case Details">
          {selected ? (
            <div className="text-sm space-y-4 text-slate-200">
              <div className="space-y-2">
                <p><span className="text-slate-400">Case ID:</span> {selected.id}</p>
                <p><span className="text-slate-400">Wallet reference:</span> <span className="font-mono text-xs text-slate-300">{selected.walletRef}</span></p>
                <p><span className="text-slate-400">Title:</span> {selected.title}</p>
                <p><span className="text-slate-400">Assigned handler:</span> {selected.handler}</p>
                <p><span className="text-slate-400">Custody status:</span> <StatusBadge status={selected.custodyStatus} /></p>
              </div>

              <div>
                <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">Linked assets / coin balances</div>
                {linkedAssets.length > 0 ? (
                  <div className="space-y-2">
                    {linkedAssets.map((a) => (
                      <div key={a.id} className="rounded-md border border-slate-700/50 bg-dark-card/30 px-3 py-2 flex items-center justify-between">
                        <div className="min-w-0">
                          <div className="text-sm font-semibold text-slate-100">{a.symbol}</div>
                          <div className="text-xs text-slate-400">{a.network} · {a.id}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold tabular-nums text-slate-100">{a.balance ?? 0}</div>
                          <div className="text-xs text-slate-400"><StatusBadge status={a.status} /></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No linked assets found for this wallet reference.</p>
                )}
              </div>

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