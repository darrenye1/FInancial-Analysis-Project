import {
  ForecastChart,
  GrowthChart,
  MarginChart,
  RevenueProfitChart,
  ScenarioChart,
  StockPriceChart,
  TornadoChart,
} from "@/components/charts";
import { Footer, Header, Hero, ProfileBanner } from "@/components/layout";
import { Badge, Card, ChartImage, KPICard, Section } from "@/components/ui";
import { analysisData, formatBillions, formatPercent } from "@/lib/data";

export default function Home() {
  const { company, highlights, pl, budget, forecast, sensitivity, stockPrice, generatedAt, ticker } =
    analysisData;

  return (
    <>
      <ProfileBanner />
      <Header name={company.name} ticker={ticker} />
      <main>
        <Hero name={company.name} sector={company.sector} industry={company.industry} />

        {/* Overview */}
        <div id="overview" className="mx-auto max-w-7xl px-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KPICard
              label={`Revenue (${highlights.latestYear})`}
              value={formatBillions(highlights.revenue)}
              change={highlights.revenueYoY != null ? `YoY ${formatPercent(highlights.revenueYoY)}` : undefined}
              positive={highlights.revenueYoY != null ? highlights.revenueYoY >= 0 : undefined}
            />
            <KPICard
              label={`Net Income (${highlights.latestYear})`}
              value={formatBillions(highlights.netIncome)}
            />
            <KPICard
              label="Net Margin"
              value={highlights.netMargin != null ? `${highlights.netMargin}%` : "N/A"}
            />
            <KPICard
              label="Gross Margin"
              value={highlights.grossMargin != null ? `${highlights.grossMargin}%` : "N/A"}
            />
          </div>
        </div>

        {/* P&L */}
        <div className="mx-auto max-w-7xl px-6">
          <Section
            id="pl"
            title="P&L Analysis"
            subtitle="Revenue trends, profit margins, year-over-year growth, and expense structure from Tesla's income statement."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <RevenueProfitChart data={pl.incomeStatement} />
              <MarginChart data={pl.margins} />
              <GrowthChart data={pl.growth} />
              <StockPriceChart data={stockPrice} />
            </div>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <ChartImage src="/charts/01_revenue_profit_trend.png" alt="Revenue and profit trend" />
              <ChartImage src="/charts/02_margin_trends.png" alt="Margin trends" />
            </div>
          </Section>

          {/* Budget */}
          <Section
            id="budget"
            title="Budgeting & Variance"
            subtitle="Forward-looking budget built from historical CAGR assumptions, compared against actual performance."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <ChartImage src="/charts/05_budget_vs_actual.png" alt="Budget vs actual" />
              <Card>
                <h3 className="mb-4 text-lg font-semibold text-white">
                  Budget vs Actual — {highlights.latestYear}
                </h3>
                {budget.variance.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-brand-border text-left text-brand-muted">
                          <th className="pb-3 pr-4">Metric</th>
                          <th className="pb-3 pr-4">Budget</th>
                          <th className="pb-3 pr-4">Actual</th>
                          <th className="pb-3 pr-4">Variance</th>
                          <th className="pb-3">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {budget.variance.map((row) => (
                          <tr key={String(row.Metric)} className="border-b border-brand-border/40">
                            <td className="py-3 pr-4 text-white">{String(row.Metric)}</td>
                            <td className="py-3 pr-4 text-brand-muted">
                              {formatBillions(row.Budget as number)}
                            </td>
                            <td className="py-3 pr-4 text-brand-muted">
                              {formatBillions(row.Actual as number)}
                            </td>
                            <td
                              className={`py-3 pr-4 font-medium ${
                                (row["Variance %"] as number) >= 0 ? "text-emerald-400" : "text-red-400"
                              }`}
                            >
                              {formatPercent(row["Variance %"] as number)}
                            </td>
                            <td className="py-3">
                              <Badge>{String(row.Status)}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-brand-muted">No variance data available.</p>
                )}
              </Card>
            </div>
          </Section>

          {/* Forecast */}
          <Section
            id="forecast"
            title="Forecasting"
            subtitle="Revenue projections using exponential smoothing, with bull / base / bear scenario modeling."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <ForecastChart data={forecast.revenue} />
              <ScenarioChart data={forecast.scenarios} />
            </div>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <ChartImage src="/charts/06_revenue_forecast.png" alt="Revenue forecast" />
              <ChartImage src="/charts/07_scenario_forecast.png" alt="Scenario forecast" />
            </div>
          </Section>

          {/* Sensitivity */}
          <Section
            id="sensitivity"
            title="Sensitivity Analysis"
            subtitle="Identify which financial drivers have the greatest impact on net income under ±10% changes."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <TornadoChart data={sensitivity.tornado} />
              <ChartImage src="/charts/09_sensitivity_heatmap.png" alt="Sensitivity heatmap" />
            </div>
            <div className="mt-6">
              <Card>
                <h3 className="mb-4 text-lg font-semibold text-white">Driver Impact Ranking</h3>
                <div className="space-y-4">
                  {sensitivity.tornado.map((row, i) => (
                    <div key={row.Driver} className="flex items-center gap-4">
                      <span className="w-6 text-sm font-bold text-brand-muted">#{i + 1}</span>
                      <div className="flex-1">
                        <div className="mb-1 flex justify-between text-sm">
                          <span className="text-white">{row.Driver}</span>
                          <span className="text-brand-muted">Range: {formatBillions(row.Range)}</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-brand-border">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-brand-red to-red-400"
                            style={{
                              width: `${(row.Range / sensitivity.tornado[0].Range) * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </Section>

          {/* Methodology */}
          <Section
            id="methodology"
            title="Methodology"
            subtitle="How this analysis was built — suitable for replication on any public company."
          >
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[
                { title: "Data Source", desc: "Yahoo Finance API via yfinance — income statement, balance sheet, cash flow, and 5Y stock prices." },
                { title: "P&L Analysis", desc: "Margin trends, YoY growth rates, and expense breakdown as % of revenue." },
                { title: "Budgeting", desc: "CAGR-based forward budget with formal variance analysis (budget vs actual)." },
                { title: "Forecasting", desc: "Exponential smoothing for base forecast; bull/base/bear scenarios at ±25% / 10% / -5%." },
              ].map((item) => (
                <Card key={item.title}>
                  <h4 className="font-semibold text-white">{item.title}</h4>
                  <p className="mt-2 text-sm text-brand-muted">{item.desc}</p>
                </Card>
              ))}
            </div>
          </Section>
        </div>
      </main>
      <Footer generatedAt={generatedAt} />
    </>
  );
}
