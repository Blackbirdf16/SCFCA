import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

const STORAGE_KEY = "scfca_user";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function loadUserFromStorage(): User | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => loadUserFromStorage());

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      login: (nextUser: User) => {
        setUser(nextUser);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser));
      },
      logout: () => {
        setUser(null);
        localStorage.removeItem(STORAGE_KEY);
      }
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}