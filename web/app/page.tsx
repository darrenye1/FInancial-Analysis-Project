import {
  CCCChart,
  DuPontChart,
  ExpenseBreakdownChart,
  FCFChart,
  ForecastChart,
  GrowthChart,
  MarginBridgeChart,
  MarginChart,
  OneWaySensitivityChart,
  RevenueProfitChart,
  ScenarioChart,
  BudgetVsActualChart,
  TornadoChart,
} from "@/components/charts";
import { Footer, Header, Hero, ProfileBanner } from "@/components/layout";
import { Badge, Card, KPICard, Section } from "@/components/ui";
import { analysisData, formatBillions, formatPercent } from "@/lib/data";

export default function Home() {
  const { company, highlights, pl, budget, forecast, sensitivity, corpFin, summary, generatedAt, ticker } =
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
              label={`Free Cash Flow (${highlights.latestYear})`}
              value={highlights.freeCashFlow != null ? formatBillions(highlights.freeCashFlow) : "N/A"}
            />
            <KPICard
              label="ROE"
              value={highlights.roe != null ? `${highlights.roe}%` : "N/A"}
            />
            <KPICard
              label="Cash Conversion Cycle"
              value={highlights.cashConversionCycle != null ? `${highlights.cashConversionCycle} days` : "N/A"}
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
              <ExpenseBreakdownChart data={pl.expenseBreakdown} />
              <MarginBridgeChart data={corpFin.marginBridge} />
            </div>
          </Section>

          {/* Cash Flow */}
          <Section
            id="cashflow"
            title="Cash Flow Analysis"
            subtitle="Operating cash flow, free cash flow, and cash conversion quality — core FP&A metrics for liquidity planning."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <FCFChart data={corpFin.cashFlow} />
              <Card>
                <h3 className="mb-4 text-lg font-semibold text-white">Cash Flow Metrics</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-brand-border text-left text-brand-muted">
                        <th className="pb-3 pr-4">Year</th>
                        <th className="pb-3 pr-4">OCF</th>
                        <th className="pb-3 pr-4">FCF</th>
                        <th className="pb-3 pr-4">FCF Margin</th>
                        <th className="pb-3">OCF / NI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {corpFin.cashFlow.map((row) => (
                        <tr key={String(row.year)} className="border-b border-brand-border/40">
                          <td className="py-3 pr-4 text-white">{row.year}</td>
                          <td className="py-3 pr-4 text-brand-muted">{formatBillions(row["Operating Cash Flow"] as number)}</td>
                          <td className="py-3 pr-4 text-brand-muted">{formatBillions(row["Free Cash Flow"] as number)}</td>
                          <td className="py-3 pr-4 text-brand-muted">{row["FCF Margin %"]}%</td>
                          <td className="py-3 text-brand-muted">{row["OCF / Net Income"]}x</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          </Section>

          {/* Corporate Finance */}
          <Section
            id="corpfin"
            title="Corporate Finance & Working Capital"
            subtitle="DuPont ROE decomposition, working capital efficiency, and capital structure — standard corp fin FP&A toolkit."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <DuPontChart data={corpFin.dupont} />
              <CCCChart data={corpFin.workingCapital} />
            </div>
            <div className="mt-6">
              <Card>
                <h3 className="mb-4 text-lg font-semibold text-white">Capital Structure</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-brand-border text-left text-brand-muted">
                        <th className="pb-3 pr-4">Year</th>
                        <th className="pb-3 pr-4">Net Debt</th>
                        <th className="pb-3 pr-4">Debt / Equity</th>
                        <th className="pb-3 pr-4">Net Debt / EBITDA</th>
                        <th className="pb-3">Interest Coverage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {corpFin.capitalStructure.map((row) => (
                        <tr key={String(row.year)} className="border-b border-brand-border/40">
                          <td className="py-3 pr-4 text-white">{row.year}</td>
                          <td className="py-3 pr-4 text-brand-muted">{formatBillions(row["Net Debt"] as number)}</td>
                          <td className="py-3 pr-4 text-brand-muted">{row["Debt / Equity"]}x</td>
                          <td className="py-3 pr-4 text-brand-muted">{row["Net Debt / EBITDA"]}x</td>
                          <td className="py-3 text-brand-muted">{row["Interest Coverage"]}x</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          </Section>

          {/* Budget */}
          <Section
            id="budget"
            title="Budgeting & Variance"
            subtitle="Forward-looking budget built from historical CAGR assumptions, compared against actual performance."
          >
            <div className="grid gap-6 lg:grid-cols-2">
              <BudgetVsActualChart data={budget.summary} />
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
          </Section>

          {/* Sensitivity */}
          <Section
            id="sensitivity"
            title="Sensitivity Analysis"
            subtitle="Identify which financial drivers have the greatest impact on net income under ±10% changes."
          >
            <TornadoChart data={sensitivity.tornado} />
            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <OneWaySensitivityChart data={sensitivity.oneWay} />
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

          {/* Executive Summary Report */}
          <Section
            id="summary"
            title="Executive Summary"
            subtitle="Narrative FP&A report synthesizing key findings across P&L, cash flow, working capital, budgeting, forecasting, and sensitivity analysis."
          >
            <div className="space-y-6">
              {summary.sections.map((section) => (
                <Card key={section.title}>
                  <h3 className="mb-3 text-base font-semibold text-brand-accent">{section.title}</h3>
                  <p className="text-sm leading-relaxed text-brand-muted">{section.body}</p>
                </Card>
              ))}
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
                { title: "Data Source", desc: "Yahoo Finance — income statement, balance sheet, and cash flow for integrated FP&A modeling." },
                { title: "P&L & Margin Bridge", desc: "Revenue, margin, and OpEx decomposition of year-over-year net income changes." },
                { title: "Cash Flow & FCF", desc: "Operating cash flow, free cash flow, FCF margin, and earnings quality (OCF/NI)." },
                { title: "Corp Fin Metrics", desc: "DuPont ROE, cash conversion cycle, net debt/EBITDA, and interest coverage." },
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
