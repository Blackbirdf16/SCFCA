import { useLocation } from "react-router-dom";
import { useMemo, useState } from "react";
import { useAuth } from "../hooks/useAuth";

function titleFromPath(pathname: string): string {
  if (pathname.startsWith("/dashboard")) return "Dashboard";
  if (pathname.startsWith("/cases")) return "Cases";
  if (pathname.startsWith("/assets")) return "Assets";
  if (pathname.startsWith("/tickets")) return "Tickets";
  if (pathname.startsWith("/audit")) return "Audit";
  if (pathname.startsWith("/documents")) return "Documents";
  if (pathname.startsWith("/account")) return "Account";
  if (pathname.startsWith("/settings")) return "Settings";
  if (pathname.startsWith("/help")) return "Help / Chat";
  return "SCFCA";
}

function deriveUid(seed: string): string {
  let hash = 0;
  for (const ch of seed) {
    const cp = ch.codePointAt(0) ?? 0;
    hash = Math.trunc(hash * 31 + cp);
    hash = hash % 2147483647;
  }
  return Math.abs(hash).toString(36).toUpperCase().padStart(8, "0").slice(0, 8);
}

export default function Header() {
  const location = useLocation();
  const { user } = useAuth();
  const [query, setQuery] = useState("");

  const uid = useMemo(() => {
    const seed = `${user?.username ?? "demo"}:${user?.role ?? "unknown"}:${user?.token ?? ""}`;
    return deriveUid(seed);
  }, [user?.role, user?.token, user?.username]);

  return (
    <header className="h-16 border-b border-slate-700/50 bg-dark-panel px-6 flex items-center gap-4">
      <div className="flex items-baseline gap-3 min-w-0">
        <h2 className="text-lg font-semibold tracking-tight text-slate-100 truncate">
          {titleFromPath(location.pathname)}
        </h2>
        <div className="hidden lg:block text-xs text-slate-500">Institutional custody PoC</div>
      </div>

      <div className="flex-1 hidden md:block">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search cases, wallet refs, documents…"
          className="w-full max-w-xl rounded-md bg-dark-card/40 border border-slate-600/30 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-400/60 transition"
        />
      </div>

      <div className="ml-auto flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2">
          <button
            type="button"
            className="px-3 py-2 text-sm rounded-md border border-slate-600/40 bg-slate-700/10 hover:bg-slate-700/25 transition text-slate-100"
          >
            Help
          </button>
          <button
            type="button"
            className="px-3 py-2 text-sm rounded-md border border-slate-600/40 bg-slate-700/10 hover:bg-slate-700/25 transition text-slate-100"
          >
            Chat
          </button>
        </div>

        <div className="text-right leading-tight">
          <div className="text-sm font-semibold text-slate-100">
            {user?.username ?? "demo"}
          </div>
          <div className="text-[11px] text-slate-500">
            <span>UID </span>
            <span className="text-slate-300 font-semibold">{uid}</span>
            <span className="mx-1">·</span>
            <span>{user?.role ?? "unknown"}</span>
          </div>
        </div>
      </div>
    </header>
  );
}