import { useMemo, useState } from "react";
import TableWrapper from "../components/TableWrapper";
import { demoAudit } from "../services/data";
import { useAuth } from "../hooks/useAuth";
import { canViewAudit } from "../utils/roles";

export default function Audit() {
  const [filter, setFilter] = useState("");
  const { user } = useAuth();

  const filtered = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) return demoAudit;
    return demoAudit.filter(
      (item) =>
        item.actor.toLowerCase().includes(query) ||
        item.action.toLowerCase().includes(query) ||
        item.timestamp.toLowerCase().includes(query)
    );
  }, [filter]);

  if (!user || !canViewAudit(user.role)) {
    return (
      <div className="panel p-5 text-sm text-slate-300">
        Audit view is restricted to administrator and auditor roles.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="panel p-4">
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter by actor, action, or timestamp"
          className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
        />
      </div>

      <TableWrapper title="Audit Events">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-400 border-b border-slate-700">
              <th className="py-2">Event ID</th>
              <th className="py-2">Timestamp</th>
              <th className="py-2">Actor</th>
              <th className="py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((item) => (
              <tr key={item.id} className="border-b border-slate-800">
                <td className="py-2">{item.id}</td>
                <td className="py-2">{item.timestamp}</td>
                <td className="py-2">{item.actor}</td>
                <td className="py-2">{item.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableWrapper>
    </div>
  );
}