import { AssetStatus, TicketStatus } from "../types";

type BadgeStatus = TicketStatus | AssetStatus | "open" | "in_review" | "closed";

const classes: Record<BadgeStatus, string> = {
  pending: "bg-amber-500/20 text-amber-300 border border-amber-400/40",
  approved: "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40",
  rejected: "bg-rose-500/20 text-rose-300 border border-rose-400/40",
  active: "bg-sky-500/20 text-sky-300 border border-sky-400/40",
  inactive: "bg-slate-500/20 text-slate-300 border border-slate-400/40",
  open: "bg-indigo-500/20 text-indigo-300 border border-indigo-400/40",
  in_review: "bg-amber-500/20 text-amber-300 border border-amber-400/40",
  closed: "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40"
};

export default function StatusBadge({ status }: { status: BadgeStatus }) {
  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded-md ${classes[status]}`}>
      {status.replace("_", " ")}
    </span>
  );
}