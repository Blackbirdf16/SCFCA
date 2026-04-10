import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
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
      const user = await authService.login({ username, password });
      login(user);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      console.error(err);
      setError("Login failed. Check backend status and credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark px-4">
      <form onSubmit={handleSubmit} className="panel p-8 w-full max-w-md">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-100 mb-1">
          <span className="text-gold">SCFCA</span> Control Panel
        </h1>
        <p className="text-sm text-slate-400 mb-6">Institutional custody thesis demo</p>
        <input
          className="w-full mb-4 p-3 rounded bg-dark-card/50 text-slate-100 border border-slate-600/40 focus:border-slate-400/60 transition"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="w-full mb-4 p-3 rounded bg-dark-card/50 text-slate-100 border border-slate-600/40 focus:border-slate-400/60 transition"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <div className="text-red-400 mb-2">{error}</div>}
        <button
          type="submit"
          disabled={loading}
          className="accent-button w-full py-3 font-semibold disabled:opacity-60"
        >
          {loading ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
