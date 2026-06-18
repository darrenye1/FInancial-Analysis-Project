"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "./ui";
import { formatBillions } from "@/lib/format";

const COLORS = ["#CC0000", "#e94560", "#3498db", "#2ecc71"];

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string }) {
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

export function RevenueProfitChart({ data }: { data: Record<string, number | string | null>[] }) {
  const chartData = data.filter((d) => d["Total Revenue"] != null);
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Revenue & Profitability</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <Bar dataKey="Total Revenue" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
          <Bar dataKey="Gross Profit" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
          <Bar dataKey="Operating Income" fill={COLORS[2]} radius={[4, 4, 0, 0]} />
          <Bar dataKey="Net Income" fill={COLORS[3]} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function MarginChart({ data }: { data: Record<string, number | string | null>[] }) {
  const keys = Object.keys(data[0] || {}).filter((k) => k !== "year");
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Profit Margins (%)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip />
          <Legend />
          {keys.map((key, i) => (
            <Line key={key} type="monotone" dataKey={key} stroke={COLORS[i % COLORS.length]} strokeWidth={2.5} dot={{ r: 4 }} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function ForecastChart({ data }: { data: Record<string, number | string | null>[] }) {
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Revenue Forecast</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="Year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Line
            type="monotone"
            dataKey="Total Revenue"
            stroke="#CC0000"
            strokeWidth={2.5}
            dot={(props: { cx?: number; cy?: number; payload?: { Type?: string } }) => {
              const { cx, cy, payload } = props;
              if (cx == null || cy == null) return <></>;
              const color = payload?.Type === "Forecast" ? "#3498db" : "#CC0000";
              return <circle cx={cx} cy={cy} r={5} fill={color} />;
            }}
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

  const scenarioColors: Record<string, string> = { Bear: "#e74c3c", Base: "#95a5a6", Bull: "#2ecc71" };

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Scenario Analysis</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          {scenarios.map((s) => (
            <Line key={s} type="monotone" dataKey={s} stroke={scenarioColors[s]} strokeWidth={2.5} dot={{ r: 4 }} />
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
          <Line type="monotone" dataKey="close" stroke="#CC0000" strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function TornadoChart({
  data,
}: {
  data: { Driver: string; "Low Case": number; "High Case": number; Base: number; Range: number }[];
}) {
  const chartData = data.map((d) => ({
    driver: d.Driver.replace("Total ", "").replace("Cost Of Revenue", "COGS"),
    low: d["Low Case"] - d.Base,
    high: d["High Case"] - d.Base,
    base: d.Base,
  }));

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Sensitivity Tornado — Net Income</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis type="number" tickFormatter={(v) => `$${(v / 1e9).toFixed(1)}B`} stroke="#8892a4" />
          <YAxis type="category" dataKey="driver" width={80} stroke="#8892a4" tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => formatBillions(Math.abs(Number(v)))} />
          <Bar dataKey="low" stackId="a" fill="#e74c3c" />
          <Bar dataKey="high" stackId="a" fill="#2ecc71" />
        </BarChart>
      </ResponsiveContainer>
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
      <h3 className="mb-4 text-lg font-semibold text-white">Year-over-Year Growth (%)</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip />
          <Legend />
          {keys.map((key, i) => (
            <Bar key={key} dataKey={key} name={key.replace(" YoY %", "")} radius={[4, 4, 0, 0]}>
              {chartData.map((entry, idx) => (
                <Cell
                  key={idx}
                  fill={(entry[key] as number) >= 0 ? "#2ecc71" : "#e74c3c"}
                  opacity={i === 0 ? 1 : 0.7}
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
  const keys = ["Operating Cash Flow", "Free Cash Flow"];
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Operating & Free Cash Flow</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          {keys.map((key, i) => (
            <Line key={key} type="monotone" dataKey={key} stroke={COLORS[i]} strokeWidth={2.5} dot={{ r: 4 }} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function DuPontChart({ data }: { data: Record<string, number | string | null>[] }) {
  const keys = ["ROE %", "ROA %", "ROIC %"];
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Return Metrics (DuPont)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" unit="%" />
          <Tooltip />
          <Legend />
          {keys.map((key, i) => (
            <Line key={key} type="monotone" dataKey={key} stroke={COLORS[i]} strokeWidth={2.5} dot={{ r: 4 }} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function CCCChart({ data }: { data: Record<string, number | string | null>[] }) {
  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Cash Conversion Cycle (days)</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="year" stroke="#8892a4" />
          <YAxis stroke="#8892a4" />
          <Tooltip />
          <Bar dataKey="Cash Conversion Cycle" fill="#3498db" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function MarginBridgeChart({ data }: { data: Record<string, number | string | null>[] }) {
  if (!data.length) return null;
  const latest = data[data.length - 1];
  const keys = ["Revenue Volume", "Margin / Mix", "OpEx Change", "Below-the-Line"];
  const chartData = keys.map((k) => ({ name: k.replace(" / Mix", ""), value: latest[k] as number }));

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">
        Net Income Bridge — {String(latest.period)}
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="name" stroke="#8892a4" tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(1)}B`} stroke="#8892a4" />
          <Tooltip formatter={(v) => formatBillions(Number(v))} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.value >= 0 ? "#2ecc71" : "#e74c3c"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function BudgetVsActualChart({ data }: { data: Record<string, number | string | null>[] }) {
  const chartData = data
    .filter((d) => d["Total Revenue"] != null)
    .map((d) => {
      const fiscalYear = d.fiscalYear ?? d.Year ?? d.year;
      const type = String(d.Type ?? "Actual");
      return {
        ...d,
        label: String(d.label ?? `${fiscalYear} ${type}`),
      };
    });

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold text-white">Revenue: Actual vs Budget</h3>
      <p className="mb-3 text-xs text-brand-muted">
        Red = Actual (historical) · Blue = Budget (forward projection from {chartData.find((d) => d.Type === "Budget")?.fiscalYear ?? "base year"} base)
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis dataKey="label" stroke="#8892a4" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={50} />
          <YAxis tickFormatter={(v) => `$${(v / 1e9).toFixed(0)}B`} stroke="#8892a4" />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload as Record<string, unknown>;
              return (
                <div className="rounded-lg border border-brand-border bg-brand-dark/95 px-4 py-3 shadow-xl">
                  <p className="text-sm font-medium text-white">{String(d.label)}</p>
                  <p className="text-sm text-brand-muted">Type: {String(d.Type)}</p>
                  <p className="text-sm" style={{ color: payload[0].color }}>
                    Revenue: {formatBillions(d["Total Revenue"] as number)}
                  </p>
                </div>
              );
            }}
          />
          <Legend formatter={(value) => `${value} (see bar color)`} />
          <Bar dataKey="Total Revenue" name="Revenue" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.Type === "Budget" ? "#3498db" : "#CC0000"}
                opacity={entry.Type === "Budget" ? 0.85 : 1}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
