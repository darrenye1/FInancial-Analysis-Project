import { BarChart3, Calculator, LineChart, TrendingUp, Zap } from "lucide-react";
import { Badge } from "./ui";

const links = [
  { href: "#overview", label: "Overview", icon: TrendingUp },
  { href: "#pl", label: "P&L", icon: BarChart3 },
  { href: "#budget", label: "Budget", icon: Calculator },
  { href: "#forecast", label: "Forecast", icon: LineChart },
  { href: "#sensitivity", label: "Sensitivity", icon: Zap },
];

export function Header({ name, ticker }: { name: string; ticker: string }) {
  return (
    <header className="sticky top-0 z-50 border-b border-brand-border/60 bg-brand-dark/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-red font-display text-lg font-bold text-white">
            T
          </div>
          <div>
            <h1 className="font-display text-lg font-bold text-white">{name}</h1>
            <p className="text-xs text-brand-muted">{ticker} · Financial Analysis</p>
          </div>
        </div>
        <nav className="hidden items-center gap-1 md:flex">
          {links.map(({ href, label, icon: Icon }) => (
            <a
              key={href}
              href={href}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-brand-muted transition hover:bg-white/5 hover:text-white"
            >
              <Icon size={14} />
              {label}
            </a>
          ))}
        </nav>
        <Badge>Portfolio Project</Badge>
      </div>
    </header>
  );
}

export function Hero({
  name,
  sector,
  industry,
}: {
  name: string;
  sector: string;
  industry: string;
}) {
  return (
    <div className="relative overflow-hidden py-20">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-red/20 via-transparent to-transparent" />
      <div className="relative mx-auto max-w-7xl px-6">
        <p className="mb-4 text-sm font-medium uppercase tracking-widest text-red-400">
          Financial Analysis Project
        </p>
        <h1 className="font-display text-5xl font-bold tracking-tight text-white md:text-6xl">
          {name}
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-brand-muted">
          End-to-end financial modeling with real Yahoo Finance data — P&L analysis, budgeting,
          forecasting, and sensitivity analysis built with Python &amp; React.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <span className="rounded-full bg-white/5 px-4 py-1.5 text-sm text-brand-muted ring-1 ring-white/10">
            {sector}
          </span>
          <span className="rounded-full bg-white/5 px-4 py-1.5 text-sm text-brand-muted ring-1 ring-white/10">
            {industry}
          </span>
          <span className="rounded-full bg-white/5 px-4 py-1.5 text-sm text-brand-muted ring-1 ring-white/10">
            Python · yfinance · Next.js
          </span>
        </div>
      </div>
    </div>
  );
}

export function Footer({ generatedAt }: { generatedAt: string }) {
  return (
    <footer className="border-t border-brand-border py-10 text-center text-sm text-brand-muted">
      <p>Data sourced from Yahoo Finance · For educational purposes only</p>
      <p className="mt-1">Last updated: {new Date(generatedAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</p>
    </footer>
  );
}
