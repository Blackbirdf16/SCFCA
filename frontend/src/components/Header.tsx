import { useLocation } from "react-router-dom";

function titleFromPath(pathname: string): string {
  if (pathname.startsWith("/dashboard")) return "Dashboard";
  if (pathname.startsWith("/cases")) return "Cases";
  if (pathname.startsWith("/assets")) return "Assets";
  if (pathname.startsWith("/tickets")) return "Tickets";
  if (pathname.startsWith("/audit")) return "Audit";
  if (pathname.startsWith("/documents")) return "Documents";
  return "SCFCA";
}

export default function Header() {
  const location = useLocation();

  return (
    <header className="h-16 border-b border-slate-700/50 bg-dark-panel px-6 flex items-center justify-between">
      <h2 className="text-lg font-semibold text-slate-100">{titleFromPath(location.pathname)}</h2>
      <div className="text-xs text-slate-400">Institutional Secure Custody Demo</div>
    </header>
  );
}