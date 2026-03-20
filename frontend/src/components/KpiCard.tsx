interface KpiCardProps {
  title: string;
  value: string | number;
}

export default function KpiCard({ title, value }: Readonly<KpiCardProps>) {
  return (
    <div className="panel p-5">
      <p className="text-[11px] uppercase tracking-wide text-slate-400">{title}</p>
      <p className="text-3xl mt-2 font-semibold tabular-nums text-slate-100">{value}</p>
    </div>
  );
}