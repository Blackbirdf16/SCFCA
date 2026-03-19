import type { ReactNode } from "react";
import { useAuth } from "../hooks/useAuth";
import { Role } from "../types";

interface RoleGuardProps {
  allow: Role[];
  children: ReactNode;
  fallback?: ReactNode;
}

export default function RoleGuard({ allow, children, fallback = null }: RoleGuardProps) {
  const { user } = useAuth();
  if (!user || !allow.includes(user.role)) {
    return <>{fallback}</>;
  }
  return <>{children}</>;
}