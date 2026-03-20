import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";
import { useAuth } from "../hooks/useAuth";
import { Role } from "../types";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("case_handler");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!username || !password) {
      setError("Username and password are required.");
      return;
    }

    setLoading(true);
    try {
      const user = await authService.login({ username, password, role });
      login(user);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError("Login failed. Check backend status and credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark px-4">
      <form onSubmit={handleSubmit} className="bg-dark-panel border border-slate-700/60 p-8 rounded-xl shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-gold mb-1">SCFCA Control Panel</h1>
        <p className="text-sm text-slate-400 mb-6">Institutional custody thesis demo</p>
        <input
          className="w-full mb-4 p-3 rounded bg-dark text-white border border-gray-700"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="w-full mb-4 p-3 rounded bg-dark text-white border border-gray-700"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <select
          className="w-full mb-4 p-3 rounded bg-dark text-white border border-gray-700"
          value={role}
          onChange={(e) => setRole(e.target.value as Role)}
        >
          <option value="case_handler">case_handler</option>
          <option value="administrator">administrator</option>
          <option value="auditor">auditor</option>
        </select>

        {error && <div className="text-red-400 mb-2">{error}</div>}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded bg-gold text-dark font-bold hover:bg-yellow-400 transition disabled:opacity-60"
        >
          {loading ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
