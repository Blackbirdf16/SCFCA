interface KpiCardProps {
  title: string;
  value: string | number;
}

export default function KpiCard({ title, value }: KpiCardProps) {
  return (
    <div className="panel p-5">
      <p className="text-xs uppercase tracking-wide text-slate-400">{title}</p>
      <p className="text-3xl mt-2 font-bold text-gold">{value}</p>
    </div>
  );
}