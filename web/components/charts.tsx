"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "./ui";
import { formatBillions } from "@/lib/format";

const PALETTE = {
  primary: "#CC0000",
  secondary: "#3498db",
  positive: "#2ecc71",
  negative: "#e74c3c",
  forecast: "#3498db",
  neutral: "#95a5a6",
  accent: "#e94560",
  tornadoLow: "#3498db",
  tornadoHigh: "#e67e22",
};

const METRIC_COLORS: Record<string, string> = {
  "Total Revenue": PALETTE.primary,
  "Gross Profit": PALETTE.accent,
  "Operating Income": PALETTE.secondary,
  "Net Income": PALETTE.positive,
  Actual: PALETTE.primary,
  Budget: PALETTE.secondary,
  Bear: PALETTE.negative,
  Base: PALETTE.neutral,
  Bull: PALETTE.positive,
  "Operating Cash Flow": PALETTE.positive,
  "Capital Expenditure": PALETTE.negative,
  "Free Cash Flow": PALETTE.secondary,
};

function shortDriver(name: string): string {
  return name.replace("Total ", "").replace("Cost Of Revenue", "COGS");
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string; payload?: Record<string, unknown> }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-brand-border bg-brand-dark/95 px-4 py-3 shadow-xl">
      <p className="mb-2 text-sm font-medium text-white">{label}</p>
      {payload.map((p) => (
        <p key={p.name} className="text-sm" style={{ color: p.color }}>
          {p.name}: {formatBillions(p.value)}
        </p>
      ))}
    </div>
  );
}

function ChartSubtitle({ children }: { children: React.ReactNode }) {
  return <p className="mb-3 text-xs text-brand-muted">{children}</p>;
}

export function RevenueProfitChart({ data }: { data: Record<string, number | string | null>[] }) {
  const chartData = data.filter((d) => d["Total Revenue"] != null);
  const metrics = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"];

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Revenue & Profitability</h3>
      <ChartSubtitle>Grouped bars by fiscal year — standard P&amp;L stack view ($B).</ChartSubtitle>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData} barCategoryGap="18%" barGap={4}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" vertical={false} />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <ReferenceLine y={0} stroke="#555" strokeDasharray="3 3" />
          {metrics.map((key) => (
            <Bar key={key} dataKey={key} fill={METRIC_COLORS[key]} radius={[3, 3, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function MarginChart({ data }: { data: Record<string, number | string | null>[] }) {
  const keys = Object.keys(data[0] || {}).filter((k) => k !== "year");
  const lineColors = [PALETTE.primary, PALETTE.accent, PALETTE.secondary, PALETTE.positive];

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Profit Margins (%)</h3>
      <ChartSubtitle>Gross, operating, and net margin trends — margin bridge inputs.</ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
          <Legend />
          <ReferenceLine y={0} stroke="#555" strokeDasharray="3 3" />
          {keys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={lineColors[i % lineColors.length]}
              strokeWidth={2.5}
              dot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function ForecastChart({ data }: { data: Record<string, number | string | null>[] }) {
  const actual = data.filter((d) => d.Type === "Actual");
  const forecast = data.filter((d) => d.Type === "Forecast");
  const lastActual = actual[actual.length - 1];
  const bridge =
    lastActual && forecast.length
      ? [
          { year: lastActual.year, "Total Revenue": lastActual["Total Revenue"], segment: "bridge" },
          { year: forecast[0].year, "Total Revenue": forecast[0]["Total Revenue"], segment: "bridge" },
        ]
      : [];

  const actualSeries = actual.map((d) => ({ ...d, segment: "actual" }));
  const forecastSeries = forecast.map((d) => ({ ...d, segment: "forecast" }));

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Revenue Forecast</h3>
      <ChartSubtitle>
        Solid = historical actuals · Dashed = exponential-smoothing projection (FP&amp;A base case).
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis
            dataKey="year"
            stroke="#8892a4"
            allowDuplicatedCategory={false}
            type="category"
          />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <Line
            data={actualSeries}
            type="monotone"
            dataKey="Total Revenue"
            name="Actual"
            stroke={PALETTE.primary}
            strokeWidth={2.5}
            dot={{ r: 5, fill: PALETTE.primary }}
            connectNulls
          />
          {bridge.length > 0 && (
            <Line
              data={bridge}
              type="monotone"
              dataKey="Total Revenue"
              name="Projection link"
              stroke={PALETTE.forecast}
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
              legendType="none"
            />
          )}
          <Line
            data={forecastSeries}
            type="monotone"
            dataKey="Total Revenue"
            name="Forecast"
            stroke={PALETTE.forecast}
            strokeWidth={2.5}
            strokeDasharray="6 4"
            dot={{ r: 5, fill: PALETTE.forecast }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function ExpenseBreakdownChart({ data }: { data: Record<string, number | string | null>[] }) {
  const keys = Object.keys(data[0] || {}).filter((k) => k !== "year");
  const lineColors = [PALETTE.negative, PALETTE.accent, PALETTE.secondary];

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Expense as % of Revenue</h3>
      <ChartSubtitle>COGS and OpEx intensity — key drivers for margin bridge and sensitivity.</ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
          <Legend />
          {keys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={lineColors[i % lineColors.length]}
              strokeWidth={2.5}
              dot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function OneWaySensitivityChart({ data }: { data: Record<string, number | null>[] }) {
  const changeKey =
    Object.keys(data[0] || {}).find((k) => k.includes("Change %")) ?? "Total Revenue Change %";
  const baseNI = data.find((d) => d[changeKey] === 0)?.["Base Net Income"] ?? data[0]?.["Base Net Income"];

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">One-Way Sensitivity — Net Income</h3>
      <ChartSubtitle>
        Revenue shock ±20% on base-year P&amp;L · dashed line = base net income (
        {baseNI != null ? formatBillions(baseNI) : "N/A"}).
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis
            dataKey={changeKey}
            stroke="#8892a4"
            tickFormatter={(v) => `${v}%`}
            label={{ value: "Revenue change (%)", position: "insideBottom", offset: -4, fill: "#8892a4" }}
          />
          <YAxis tickFormatter={(v) => `$${(Number(v) / 1e9).toFixed(1)}B`} stroke="#8892a4" />
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null;
              const row = payload[0].payload as Record<string, number>;
              return (
                <div className="rounded-lg border border-brand-border bg-brand-dark/95 px-4 py-3 shadow-xl">
                  <p className="mb-2 text-sm font-medium text-white">Revenue change: {label}%</p>
                  <p className="text-sm text-brand-muted">
                    Adjusted NI: {formatBillions(row["Adjusted Net Income"])}
                  </p>
                  <p className="text-sm" style={{ color: PALETTE.primary }}>
                    Impact: {formatBillions(row["Net Income Impact"])} (
                    {row["Net Income Impact %"]?.toFixed(1)}%)
                  </p>
                </div>
              );
            }}
          />
          {baseNI != null && (
            <ReferenceLine
              y={baseNI}
              stroke={PALETTE.neutral}
              strokeDasharray="5 5"
              label={{ value: "Base NI", fill: "#8892a4", fontSize: 11, position: "insideTopRight" }}
            />
          )}
          <Legend />
          <Line
            type="monotone"
            dataKey="Adjusted Net Income"
            name="Adjusted Net Income"
            stroke={PALETTE.primary}
            strokeWidth={2.5}
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function ScenarioChart({
  data,
}: {
  data: { Year: number; Scenario: string; "Total Revenue": number }[];
}) {
  const years = [...new Set(data.map((d) => d.Year))].sort();
  const scenarios = ["Bear", "Base", "Bull"];
  const chartData = years.map((year) => {
    const point: Record<string, number> = { year };
    for (const s of scenarios) {
      const row = data.find((d) => d.Year === year && d.Scenario === s);
      if (row) point[s] = row["Total Revenue"];
    }
    return point;
  });

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Scenario Analysis</h3>
      <ChartSubtitle>
        Bear −5% / Base +10% / Bull +25% annual revenue growth — FP&amp;A upside-downside fan.
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          {scenarios.map((s) => (
            <Line
              key={s}
              type="monotone"
              dataKey={s}
              stroke={METRIC_COLORS[s]}
              strokeWidth={2.5}
              strokeDasharray={s === "Base" ? "6 4" : undefined}
              dot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function StockPriceChart({ data }: { data: { date: string; close: number }[] }) {
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Stock Price (1Y)</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="date" stroke="#8892a4" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
          <YAxis stroke="#8892a4" domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="close" stroke={PALETTE.primary} strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

type TornadoRow = {
  Driver: string;
  "Low Case": number;
  "High Case": number;
  Base: number;
  Range: number;
};

function TornadoTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: Record<string, number | string> }[];
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-brand-border bg-brand-dark/95 px-4 py-3 shadow-xl">
      <p className="mb-2 text-sm font-medium text-white">{String(d.driver)}</p>
      <p className="text-sm" style={{ color: PALETTE.tornadoLow }}>
        Driver −10%: {formatBillions(d.lowCase as number)}
      </p>
      <p className="text-sm text-brand-muted">Base (actual): {formatBillions(d.base as number)}</p>
      <p className="text-sm" style={{ color: PALETTE.tornadoHigh }}>
        Driver +10%: {formatBillions(d.highCase as number)}
      </p>
      <p className="mt-1 text-xs text-brand-muted">Swing: {formatBillions(d.range as number)}</p>
    </div>
  );
}

export function TornadoChart({ data }: { data: TornadoRow[] }) {
  const base = data[0]?.Base ?? 0;

  const chartData = data.map((d) => {
    const lowCase = d["Low Case"];
    const highCase = d["High Case"];
    const lo = Math.min(lowCase, highCase);
    const hi = Math.max(lowCase, highCase);
    const b = d.Base;
    return {
      driver: shortDriver(d.Driver),
      lowCase,
      highCase,
      base: b,
      range: d.Range,
      spacer: lo,
      belowBase: Math.max(0, Math.min(b, hi) - lo),
      aboveBase: Math.max(0, hi - Math.max(b, lo)),
    };
  });

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Sensitivity Tornado — Net Income</h3>
      <ChartSubtitle>
        Each bar spans Low → High NI under ±10% driver shocks · vertical dashed line = base net income (
        {formatBillions(base)}).
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" horizontal={false} />
          <XAxis type="number" tickFormatter={(v) => `$${(v / 1e9).toFixed(1)}B`} stroke="#8892a4" />
          <YAxis type="category" dataKey="driver" width={88} stroke="#8892a4" tick={{ fontSize: 11 }} />
          <Tooltip content={<TornadoTooltip />} />
          <Legend
            formatter={(value) =>
              value === "belowBase"
                ? "Toward driver −10% case"
                : value === "aboveBase"
                  ? "Toward driver +10% case"
                  : value
            }
          />
          <ReferenceLine
            x={base}
            stroke={PALETTE.neutral}
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{ value: "Base", fill: "#8892a4", fontSize: 11, position: "top" }}
          />
          <Bar dataKey="spacer" stackId="range" fill="transparent" legendType="none" />
          <Bar dataKey="belowBase" stackId="range" name="belowBase" fill={PALETTE.tornadoLow} />
          <Bar dataKey="aboveBase" stackId="range" name="aboveBase" fill={PALETTE.tornadoHigh} radius={[0, 3, 3, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function DriverImpactChart({ data }: { data: TornadoRow[] }) {
  const maxRange = data[0]?.Range ?? 1;
  const base = data[0]?.Base ?? 0;

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Driver Impact Ranking</h3>
      <ChartSubtitle>
        Ranked by |High − Low| net income swing under ±10% shocks (base {formatBillions(base)}).
      </ChartSubtitle>
      <div className="space-y-5">
        {data.map((row, i) => {
          const pct = (row.Range / maxRange) * 100;
          return (
            <div key={row.Driver}>
              <div className="mb-1.5 flex items-baseline justify-between gap-2 text-sm">
                <span className="font-medium text-white">
                  <span className="mr-2 text-brand-muted">#{i + 1}</span>
                  {shortDriver(row.Driver)}
                </span>
                <span className="text-xs text-brand-muted">Swing {formatBillions(row.Range)}</span>
              </div>
              <div className="mb-1 flex justify-between text-xs text-brand-muted">
                <span>−10%: {formatBillions(row["Low Case"])}</span>
                <span>+10%: {formatBillions(row["High Case"])}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-brand-border">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${pct}%`,
                    background: `linear-gradient(90deg, ${PALETTE.tornadoLow}, ${PALETTE.tornadoHigh})`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export function GrowthChart({ data }: { data: Record<string, number | string | null>[] }) {
  const revenueKey = Object.keys(data[0] || {}).find((k) => k.includes("Total Revenue"));
  const niKey = Object.keys(data[0] || {}).find((k) => k.includes("Net Income"));
  const keys = [revenueKey, niKey].filter(Boolean) as string[];
  const chartData = data.filter((d) => keys.some((k) => d[k] != null));

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Year-over-Year Growth (%)</h3>
      <ChartSubtitle>Grouped YoY % — green = expansion, red = contraction.</ChartSubtitle>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} barCategoryGap="22%" barGap={6}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" vertical={false} />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
          <Legend formatter={(v) => String(v).replace(" YoY %", "")} />
          <ReferenceLine y={0} stroke="#888" strokeWidth={1} />
          {keys.map((key, i) => (
            <Bar key={key} dataKey={key} name={key} radius={[3, 3, 0, 0]} opacity={i === 0 ? 1 : 0.85}>
              {chartData.map((entry, idx) => (
                <Cell
                  key={idx}
                  fill={(entry[key] as number) >= 0 ? PALETTE.positive : PALETTE.negative}
                />
              ))}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function FCFChart({ data }: { data: Record<string, number | string | null>[] }) {
  const chartData = data.filter((d) => d["Operating Cash Flow"] != null && Number(d.year) > 2021);
  const series = ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"];

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Cash Flow &amp; Free Cash Flow</h3>
      <ChartSubtitle>
        Grouped $B view — CapEx shown as absolute outflow (standard FP&amp;A presentation).
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} barCategoryGap="18%" barGap={4}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" vertical={false} />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip
            formatter={(v, name) => [
              formatBillions(Number(v)),
              name === "Capital Expenditure" ? "CapEx (outflow)" : String(name),
            ]}
          />
          <Legend formatter={(v) => (v === "Capital Expenditure" ? "CapEx (outflow)" : String(v))} />
          <ReferenceLine y={0} stroke="#555" strokeDasharray="3 3" />
          {series.map((key) => (
            <Bar
              key={key}
              dataKey={key}
              name={key}
              fill={METRIC_COLORS[key]}
              radius={[3, 3, 0, 0]}
              // CapEx stored negative in some exports; display magnitude for grouped compare
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function DuPontChart({ data }: { data: Record<string, number | string | null>[] }) {
  const keys = ["ROE %", "ROA %", "ROIC %"];
  const lineColors = [PALETTE.primary, PALETTE.secondary, PALETTE.positive];

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Return Metrics (DuPont)</h3>
      <ChartSubtitle>ROE, ROA, and ROIC — capital efficiency trends for corp fin review.</ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
          <Legend />
          <ReferenceLine y={0} stroke="#555" strokeDasharray="3 3" />
          {keys.map((key, i) => (
            <Line key={key} type="monotone" dataKey={key} stroke={lineColors[i]} strokeWidth={2.5} dot={{ r: 4 }} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function CCCChart({ data }: { data: Record<string, number | string | null>[] }) {
  const chartData = data.filter((d) => d["Cash Conversion Cycle"] != null);

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Cash Conversion Cycle</h3>
      <ChartSubtitle>CCC = DSO + DIO − DPO (days) — working capital efficiency bridge.</ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit=" days" />
          <Tooltip formatter={(v) => `${Number(v).toFixed(1)} days`} />
          <Legend />
          <ReferenceLine y={0} stroke="#888" strokeWidth={1} />
          <Bar dataKey="Cash Conversion Cycle" name="CCC" fill={PALETTE.secondary} radius={[3, 3, 0, 0]} />
          <Line type="monotone" dataKey="DSO (days)" name="DSO" stroke={PALETTE.primary} strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="DIO (days)" name="DIO" stroke={PALETTE.accent} strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="DPO (days)" name="DPO" stroke={PALETTE.positive} strokeWidth={2} dot={{ r: 3 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function MarginBridgeChart({
  data,
  closingNetIncome,
}: {
  data: Record<string, number | string | null>[];
  closingNetIncome?: number;
}) {
  if (!data.length) return null;
  const latest = data[data.length - 1];
  const period = String(latest.period ?? "");
  const totalDelta = latest["Total Δ Net Income"] as number;
  const closing = closingNetIncome;
  const opening =
    closing != null && typeof totalDelta === "number" ? closing - totalDelta : undefined;

  const components = [
    { key: "Revenue Volume", label: "Revenue Vol." },
    { key: "Margin / Mix", label: "Margin/Mix" },
    { key: "OpEx Change", label: "OpEx" },
    { key: "Below-the-Line", label: "Below Line" },
  ];

  if (opening == null || closing == null) {
    const chartData = components.map((c) => ({
      name: c.label,
      value: latest[c.key] as number,
    }));
    return (
      <Card>
        <h3 className="mb-4 text-lg font-semibold text-white">Net Income Bridge — {period}</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" vertical={false} />
            <XAxis dataKey="name" stroke="#8892a4" tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(1)}B`} stroke="#8892a4" />
            <Tooltip formatter={(v) => formatBillions(Number(v))} />
            <ReferenceLine y={0} stroke="#888" />
            <Bar dataKey="value" radius={[3, 3, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.value >= 0 ? PALETTE.positive : PALETTE.negative} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>
    );
  }

  const priorLabel = period.split("→")[0]?.trim() ?? "Prior";
  const currentLabel = period.split("→")[1]?.trim() ?? "Current";

  type WfStep = {
    label: string;
    spacer: number;
    bar: number;
    display: number;
    kind: "total" | "delta";
  };

  const steps: WfStep[] = [{ label: `NI ${priorLabel}`, spacer: 0, bar: opening, display: opening, kind: "total" }];

  let running = opening;
  for (const c of components) {
    const v = latest[c.key] as number;
    steps.push({
      label: c.label,
      spacer: v >= 0 ? running : running + v,
      bar: Math.abs(v),
      display: v,
      kind: "delta",
    });
    running += v;
  }
  steps.push({ label: `NI ${currentLabel}`, spacer: 0, bar: closing, display: closing, kind: "total" });

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Net Income Bridge — {period}</h3>
      <ChartSubtitle>
        Waterfall: opening NI {formatBillions(opening)} → bridge drivers → closing NI{" "}
        {formatBillions(closing)} (Δ {formatBillions(totalDelta)}).
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={steps} margin={{ bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" vertical={false} />
          <XAxis dataKey="label" stroke="#8892a4" tick={{ fontSize: 10 }} interval={0} angle={-12} textAnchor="end" height={56} />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(1)}B`} stroke="#8892a4" />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const row = payload[0].payload as WfStep;
              return (
                <div className="rounded-lg border border-brand-border bg-brand-dark/95 px-4 py-3 shadow-xl">
                  <p className="text-sm font-medium text-white">{row.label}</p>
                  <p className="text-sm text-brand-muted">{formatBillions(row.display)}</p>
                </div>
              );
            }}
          />
          <ReferenceLine y={0} stroke="#888" />
          <Bar dataKey="spacer" stackId="wf" fill="transparent" legendType="none" />
          <Bar dataKey="bar" stackId="wf" name="Net Income" radius={[3, 3, 0, 0]}>
            {steps.map((entry, i) => (
              <Cell
                key={i}
                fill={
                  entry.kind === "total"
                    ? PALETTE.neutral
                    : entry.display >= 0
                      ? PALETTE.positive
                      : PALETTE.negative
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function BudgetVsActualChart({ data }: { data: Record<string, number | string | null>[] }) {
  const rows = data.filter((d) => d["Total Revenue"] != null);
  const years = [...new Set(rows.map((d) => d.fiscalYear ?? d.Year ?? d.year))].sort(
    (a, b) => Number(a) - Number(b),
  );

  const chartData = years.map((year) => {
    const actual = rows.find((d) => (d.fiscalYear ?? d.Year ?? d.year) === year && d.Type === "Actual");
    const budget = rows.find((d) => (d.fiscalYear ?? d.Year ?? d.year) === year && d.Type === "Budget");
    return {
      year,
      Actual: actual?.["Total Revenue"] as number | undefined,
      Budget: budget?.["Total Revenue"] as number | undefined,
    };
  });

  const budgetBaseYear =
    rows.find((d) => d.Type === "Budget")?.fiscalYear ?? rows.find((d) => d.Type === "Actual")?.fiscalYear;

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Revenue: Actual vs Budget</h3>
      <ChartSubtitle>
        Grouped comparison by fiscal year · budget forward plan from {budgetBaseYear} stated growth assumptions.
      </ChartSubtitle>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} barCategoryGap="22%" barGap={6}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" vertical={false} />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null;
              return (
                <div className="rounded-lg border border-brand-border bg-brand-dark/95 px-4 py-3 shadow-xl">
                  <p className="mb-2 text-sm font-medium text-white">FY {label}</p>
                  {payload.map((p) =>
                    p.value != null ? (
                      <p key={p.name} className="text-sm" style={{ color: p.color }}>
                        {p.name}: {formatBillions(Number(p.value))}
                      </p>
                    ) : null,
                  )}
                </div>
              );
            }}
          />
          <Legend />
          <Bar dataKey="Actual" name="Actual" fill={METRIC_COLORS.Actual} radius={[3, 3, 0, 0]} />
          <Bar dataKey="Budget" name="Budget" fill={METRIC_COLORS.Budget} radius={[3, 3, 0, 0]} opacity={0.85} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function TwoWaySensitivityHeatmap({
  data,
}: {
  data: { columns: string[]; rows: Record<string, number | string | null>[] };
}) {
  const revCols = data.columns.filter((c) => c.includes("Total Revenue"));
  const opexKey = data.rows[0] ? Object.keys(data.rows[0]).find((k) => k === "change" || k.includes("OpEx")) : "change";

  const values = data.rows.flatMap((row) =>
    revCols.map((col) => (typeof row[col] === "number" ? (row[col] as number) : null)).filter((v): v is number => v != null),
  );
  const min = Math.min(...values);
  const max = Math.max(...values);
  const mid = values.reduce((a, b) => a + b, 0) / values.length;

  function cellColor(v: number): string {
    const t = max === min ? 0.5 : (v - min) / (max - min);
    if (t < 0.5) {
      const u = t * 2;
      return `rgb(${Math.round(231 + (241 - 231) * u)}, ${Math.round(76 + (196 - 76) * u)}, ${Math.round(60 + (15 - 60) * u)})`;
    }
    const u = (t - 0.5) * 2;
    return `rgb(${Math.round(241 + (46 - 241) * u)}, ${Math.round(196 + (204 - 196) * u)}, ${Math.round(15 + (113 - 15) * u)})`;
  }

  return (
    <Card>
      <h3 className="mb-1 text-lg font-semibold text-white">Two-Way Sensitivity — Net Income</h3>
      <ChartSubtitle>Revenue vs OpEx shocks → net income ($B). Green = higher NI, red = lower.</ChartSubtitle>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] border-collapse text-center text-xs">
          <thead>
            <tr>
              <th className="border border-brand-border/50 bg-brand-dark/60 p-2 text-brand-muted">OpEx ↓ / Rev →</th>
              {revCols.map((col) => (
                <th key={col} className="border border-brand-border/50 bg-brand-dark/60 p-2 text-brand-muted">
                  {col.replace("Total Revenue ", "")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row) => (
              <tr key={String(row[opexKey!])}>
                <td className="border border-brand-border/50 bg-brand-dark/40 p-2 font-medium text-white">
                  OpEx {String(row[opexKey!])}
                </td>
                {revCols.map((col) => {
                  const v = row[col] as number;
                  return (
                    <td
                      key={col}
                      className="border border-brand-border/50 p-2 font-medium text-white"
                      style={{ backgroundColor: cellColor(v) }}
                      title={formatBillions(v)}
                    >
                      ${(v / 1e9).toFixed(2)}B
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-brand-muted">
        Center of matrix ≈ {formatBillions(mid)} base-case neighborhood.
      </p>
    </Card>
  );
}
