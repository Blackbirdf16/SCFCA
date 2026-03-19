import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Role } from "../types";

const navItems = [
  { label: "Dashboard", path: "/dashboard", roles: ["case_handler", "administrator", "auditor"] as Role[] },
  { label: "Cases", path: "/cases", roles: ["case_handler", "administrator", "auditor"] as Role[] },
  { label: "Assets", path: "/assets", roles: ["case_handler", "administrator", "auditor"] as Role[] },
  { label: "Tickets", path: "/tickets", roles: ["case_handler", "administrator", "auditor"] as Role[] },
  { label: "Audit", path: "/audit", roles: ["administrator", "auditor"] as Role[] },
  { label: "Documents", path: "/documents", roles: ["case_handler", "administrator", "auditor"] as Role[] }
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const role = user?.role;

  const visibleItems = navItems.filter((item) => {
    if (!role) return false;
    return item.roles.includes(role);
  });

  return (
    <aside className="w-64 bg-dark-panel border-r border-slate-700/50 flex flex-col py-6 px-4">
      <div className="mb-8">
        <div className="text-gold text-2xl font-bold tracking-wide">SCFCA</div>
        <p className="text-xs text-slate-400 mt-1">Secure Custody Framework</p>
      </div>
      <nav className="flex-1">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block py-2.5 px-4 rounded-lg mb-2 font-medium transition ${
                isActive ? "bg-gold text-dark" : "text-gray-200 hover:bg-slate-700/50"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="pt-4 border-t border-slate-700/50 text-xs text-slate-300">
        <div className="mb-2">
          Signed in as <span className="text-gold font-semibold">{user?.username ?? "demo"}</span>
        </div>
        <div className="mb-3">
          Role <span className="text-slate-100 font-semibold">{user?.role ?? "N/A"}</span>
        </div>
        <button
          type="button"
          onClick={logout}
          className="w-full py-2 rounded-md bg-slate-700 hover:bg-slate-600 text-slate-100"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
