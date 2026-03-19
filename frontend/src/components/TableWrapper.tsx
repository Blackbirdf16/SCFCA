import type { ReactNode } from "react";

interface TableWrapperProps {
  title: string;
  children: ReactNode;
}

export default function TableWrapper({ title, children }: TableWrapperProps) {
  return (
    <section className="panel p-5">
      <h3 className="text-base font-semibold text-gold mb-4">{title}</h3>
      <div className="overflow-x-auto">{children}</div>
    </section>
  );
}