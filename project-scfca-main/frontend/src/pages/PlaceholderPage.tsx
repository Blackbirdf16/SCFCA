interface PlaceholderPageProps {
  title: string;
  description?: string;
}

export default function PlaceholderPage({ title, description }: Readonly<PlaceholderPageProps>) {
  return (
    <div className="panel p-5">
      <h1 className="text-xl font-semibold tracking-tight text-slate-100">{title}</h1>
      <p className="mt-2 text-sm text-slate-400">
        {description ?? "This view is intentionally left as a thesis-appropriate placeholder."}
      </p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-600/30 bg-dark-card/40 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-400">Purpose</div>
          <div className="mt-1 text-sm text-slate-200">
            Provide navigation structure and information architecture without over-building features.
          </div>
        </div>
        <div className="rounded-lg border border-slate-600/30 bg-dark-card/40 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-400">Next</div>
          <div className="mt-1 text-sm text-slate-200">
            Implement domain-specific data (wallet reference, holdings, transfers, and approvals) as backend APIs mature.
          </div>
        </div>
      </div>
    </div>
  );
}
