import { AssetStatus, CustodyActionStatus, TicketStatus } from "../types";

type BadgeStatus = TicketStatus | AssetStatus | CustodyActionStatus | "open" | "in_review" | "closed";

const classes: Record<BadgeStatus, string> = {
  requested: "bg-amber-500/20 text-amber-300 border border-amber-400/40",
  pending: "bg-amber-500/20 text-amber-300 border border-amber-400/40",
  pending_review: "bg-amber-500/20 text-amber-300 border border-amber-400/40",
  awaiting_second_approval: "bg-indigo-500/20 text-indigo-300 border border-indigo-400/40",
  approved: "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40",
  rejected: "bg-rose-500/20 text-rose-300 border border-rose-400/40",
  executed: "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40",
  cancelled: "bg-slate-500/20 text-slate-300 border border-slate-400/40",
  active: "bg-sky-500/20 text-sky-300 border border-sky-400/40",
  inactive: "bg-slate-500/20 text-slate-300 border border-slate-400/40",
  open: "bg-indigo-500/20 text-indigo-300 border border-indigo-400/40",
  in_review: "bg-amber-500/20 text-amber-300 border border-amber-400/40",
  closed: "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40"
};

const labels: Record<BadgeStatus, string> = {
  requested: "Requested",
  pending: "Pending",
  pending_review: "Pending review",
  awaiting_second_approval: "Awaiting 2nd approval",
  approved: "Approved",
  rejected: "Rejected",
  executed: "Executed",
  cancelled: "Cancelled",
  active: "Active",
  inactive: "Inactive",
  open: "Open",
  in_review: "In review",
  closed: "Closed"
};

export default function StatusBadge({ status }: Readonly<{ status: BadgeStatus }>) {
  return (
    <span
      className={`inline-flex items-center whitespace-nowrap px-2.5 py-1 text-[11px] font-semibold tracking-wide rounded-full ${
        classes[status]
      }`}
    >
      {labels[status] ?? String(status).replace(/_/g, " ")}
    </span>
  );
}