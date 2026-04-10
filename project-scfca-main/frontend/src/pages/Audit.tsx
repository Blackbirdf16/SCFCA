import { useEffect, useMemo, useState } from "react";
import TableWrapper from "../components/TableWrapper";
import { useAuth } from "../hooks/useAuth";
import { canViewAudit } from "../utils/roles";
import { http } from "../services/http";

interface AuditEventAPI {
  id: string;
  timestamp: string;
  actorId: string;
  eventType: string;
  action: string;
  entityType?: string;
  entityId?: string;
}

export default function Audit() {
  const [filter, setFilter] = useState("");
  const [events, setEvents] = useState<AuditEventAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await http.get("/api/v1/audit/");
        if (!cancelled) setEvents(resp.data?.events ?? []);
      } catch {
        // Fallback to empty if unauthorized or unavailable
        if (!cancelled) setEvents([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const filtered = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) return events;
    return events.filter(
      (item) =>
        item.actorId?.toLowerCase().includes(query) ||
        item.action?.toLowerCase().includes(query) ||
        item.timestamp?.toLowerCase().includes(query) ||
        item.eventType?.toLowerCase().includes(query)
    );
  }, [filter, events]);

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
          placeholder="Filter by actor, action, type, or timestamp"
          className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
        />
      </div>

      <TableWrapper title={`Audit Events (${filtered.length})`}>
        {loading ? (
          <p className="p-4 text-slate-400 text-sm">Loading audit events...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Event ID</th>
                <th className="py-2">Timestamp</th>
                <th className="py-2">Actor</th>
                <th className="py-2">Type</th>
                <th className="py-2">Action</th>
                <th className="py-2">Entity</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id} className="border-b border-slate-800">
                  <td className="py-2 font-mono text-xs">{item.id}</td>
                  <td className="py-2 text-xs">{item.timestamp}</td>
                  <td className="py-2 font-mono text-xs">{item.actorId?.slice(0, 12)}...</td>
                  <td className="py-2">{item.eventType}</td>
                  <td className="py-2">{item.action}</td>
                  <td className="py-2 text-xs">{item.entityType}:{item.entityId}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="py-4 text-center text-slate-500">No events found.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </TableWrapper>
    </div>
  );
}
