import { useMemo, useState } from "react";
import FormContainer from "../components/FormContainer";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { CaseItem } from "../types";
import { demoCases } from "../services/data";

export default function Cases() {
  const [cases, setCases] = useState<CaseItem[]>(demoCases);
  const [title, setTitle] = useState("");
  const [owner, setOwner] = useState("");
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(demoCases[0]?.id ?? null);

  const selected = useMemo(
    () => cases.find((item) => item.id === selectedCaseId) ?? null,
    [cases, selectedCaseId]
  );

  const onCreateCase = (event: React.FormEvent) => {
    event.preventDefault();
    if (!title || !owner) return;

    const newCase: CaseItem = {
      id: `C-${Math.floor(Math.random() * 900 + 100)}`,
      title,
      owner,
      status: "open"
    };
    setCases((prev) => [newCase, ...prev]);
    setTitle("");
    setOwner("");
    setSelectedCaseId(newCase.id);
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Case List">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Case ID</th>
                <th className="py-2">Title</th>
                <th className="py-2">Owner</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((item) => (
                <tr
                  key={item.id}
                  className="border-b border-slate-800 cursor-pointer hover:bg-slate-800/40"
                  onClick={() => setSelectedCaseId(item.id)}
                >
                  <td className="py-2">{item.id}</td>
                  <td className="py-2">{item.title}</td>
                  <td className="py-2">{item.owner}</td>
                  <td className="py-2"><StatusBadge status={item.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        <FormContainer title="Create Case">
          <form className="space-y-3" onSubmit={onCreateCase}>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Case title"
              className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
            />
            <input
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              placeholder="Owner"
              className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
            />
            <button className="accent-button w-full py-2" type="submit">Create</button>
          </form>
        </FormContainer>

        <FormContainer title="Case Details">
          {selected ? (
            <div className="text-sm space-y-2 text-slate-200">
              <p><span className="text-slate-400">Case ID:</span> {selected.id}</p>
              <p><span className="text-slate-400">Title:</span> {selected.title}</p>
              <p><span className="text-slate-400">Owner:</span> {selected.owner}</p>
              <p><span className="text-slate-400">Status:</span> <StatusBadge status={selected.status} /></p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">Select a case to view details.</p>
          )}
        </FormContainer>
      </div>
    </div>
  );
}