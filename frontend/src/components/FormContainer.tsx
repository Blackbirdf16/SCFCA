import type { ReactNode } from "react";

interface FormContainerProps {
  title: string;
  children: ReactNode;
}

export default function FormContainer({ title, children }: FormContainerProps) {
  return (
    <section className="panel p-5">
      <h3 className="text-base font-semibold text-gold mb-4">{title}</h3>
      <div className="space-y-3">{children}</div>
    </section>
  );
}