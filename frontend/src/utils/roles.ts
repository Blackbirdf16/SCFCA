import { Role } from "../types";

export function canApproveTickets(role: Role): boolean {
  return role === "administrator";
}

export function canViewAudit(role: Role): boolean {
  return role === "administrator" || role === "auditor";
}