import type { ReactNode } from "react";
import clsx from "clsx";

export function Section({
  id,
  title,
  subtitle,
  children,
}: {
  id: string;
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 py-16 border-t border-brand-border/50">
      <div className="mb-8">
        <h2 className="font-display text-3xl font-bold text-white">{title}</h2>
        {subtitle && <p className="mt-2 text-brand-muted max-w-2xl">{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}

export function Card({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-brand-border bg-brand-card/60 backdrop-blur-sm p-6",
        className
      )}
    >
      {children}
    </div>
  );
}

export function ChartImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Card className="overflow-hidden p-3">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={alt} className="w-full rounded-xl" />
    </Card>
  );
}

export function KPICard({
  label,
  value,
  change,
  positive,
}: {
  label: string;
  value: string;
  change?: string;
  positive?: boolean;
}) {
  return (
    <Card>
      <p className="text-sm text-brand-muted">{label}</p>
      <p className="mt-2 font-display text-2xl font-bold text-white">{value}</p>
      {change && (
        <p
          className={clsx(
            "mt-1 text-sm font-medium",
            positive === true && "text-emerald-400",
            positive === false && "text-red-400",
            positive === undefined && "text-brand-muted"
          )}
        >
          {change}
        </p>
      )}
    </Card>
  );
}

export function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full bg-brand-red/15 px-3 py-1 text-xs font-medium text-red-300 ring-1 ring-brand-red/30">
      {children}
    </span>
  );
}
