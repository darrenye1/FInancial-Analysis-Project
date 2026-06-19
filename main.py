"""
Tesla (TSLA) Financial Analysis — Main Pipeline
================================================
Runs the full analysis: data fetch → P&L → budgeting → forecasting → sensitivity.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.budgeting import BudgetAnalyzer
from src.data_fetcher import FinancialDataFetcher
from src.forecasting import FinancialForecaster
from src.pl_analysis import PLAnalyzer
from src.sensitivity import SensitivityAnalyzer
from src import visualization as viz


def run_analysis(ticker: str = "TSLA", output_dir: str = "outputs") -> None:
    out = Path(output_dir)
    data_dir = out / "data"
    charts_dir = out / "charts"
    reports_dir = out / "reports"

    for d in [data_dir, charts_dir, reports_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Financial Analysis Project — {ticker}")
    print(f"{'='*60}\n")

    # ── 1. Data Fetching ──────────────────────────────────────
    print("[1/5] Fetching data from Yahoo Finance...")
    fetcher = FinancialDataFetcher(ticker)
    info = fetcher.get_company_info()
    income_stmt = fetcher.get_income_statement()
    price_history = fetcher.get_price_history()

    fetcher.save_all(data_dir)
    print(f"      Company: {info['name']}")
    print(f"      Sector:  {info['sector']} | Industry: {info['industry']}")
    print(f"      Data years: {list(income_stmt.index)}")

    # ── 2. P&L Analysis ─────────────────────────────────────────
    print("\n[2/5] Running P&L analysis...")
    pl = PLAnalyzer(income_stmt)
    margins = pl.margin_analysis()
    growth = pl.yoy_growth()
    expense = pl.expense_breakdown()
    summary = pl.summary_table()

    summary.to_csv(reports_dir / f"{ticker}_pl_summary.csv")
    margins.to_csv(reports_dir / f"{ticker}_margins.csv")
    growth.to_csv(reports_dir / f"{ticker}_yoy_growth.csv")

    latest_year = income_stmt.index[-1]
    rev = income_stmt.loc[latest_year, "Total Revenue"]
    ni = income_stmt.loc[latest_year, "Net Income"]
    print(f"      {latest_year} Revenue: {pl.format_millions(rev)}")
    print(f"      {latest_year} Net Income: {pl.format_millions(ni)}")
    if not margins.empty:
        print(f"      Net Margin: {margins.loc[latest_year, 'Net Margin %']:.1f}%")

    viz.plot_revenue_profit_trend(income_stmt, charts_dir / "01_revenue_profit_trend.png")
    viz.plot_margin_trends(margins, charts_dir / "02_margin_trends.png")
    viz.plot_yoy_growth(growth, charts_dir / "03_yoy_growth.png")
    viz.plot_stock_price(price_history, charts_dir / "04_stock_price.png")

    # ── 3. Budgeting ────────────────────────────────────────────
    print("\n[3/5] Building budget & variance analysis...")
    budget_analyzer = BudgetAnalyzer(income_stmt)
    base_year = income_stmt.index[-2]
    budget = budget_analyzer.create_budget(
        base_year=base_year,
        growth_assumptions={"Total Revenue": 0.12, "Operating Expense": 0.08},
        years_forward=2,
    )
    budget_summary = budget_analyzer.budget_summary(
        base_year=base_year, years_forward=2, budget=budget
    )
    budget.to_csv(reports_dir / f"{ticker}_budget.csv")

    if latest_year in budget.index:
        variance = budget_analyzer.variance_analysis(budget, latest_year)
        variance.to_csv(reports_dir / f"{ticker}_variance.csv")
        print(f"      Budget vs Actual ({latest_year}):")
        for _, row in variance.iterrows():
            print(f"        {row.name}: {row['Variance %']:+.1f}% ({row['Status']})")

    viz.plot_budget_vs_actual(budget_summary, charts_dir / "05_budget_vs_actual.png")

    # ── 4. Forecasting ──────────────────────────────────────────
    print("\n[4/5] Running forecasts...")
    forecaster = FinancialForecaster(income_stmt)
    revenue_fc = forecaster.forecast_metric("Total Revenue", periods=3)
    multi_fc = forecaster.multi_metric_forecast(periods=3)
    scenarios = forecaster.scenario_forecast("Total Revenue", periods=3)

    revenue_fc.to_csv(reports_dir / f"{ticker}_revenue_forecast.csv")
    multi_fc.to_csv(reports_dir / f"{ticker}_multi_forecast.csv")
    scenarios.to_csv(reports_dir / f"{ticker}_scenarios.csv")

    fc_2028 = revenue_fc[revenue_fc["Type"] == "Forecast"].iloc[-1]["Total Revenue"]
    print(f"      Revenue forecast (last period): {pl.format_millions(fc_2028)}")

    viz.plot_forecast(revenue_fc, "Total Revenue", charts_dir / "06_revenue_forecast.png")
    viz.plot_scenario_forecast(scenarios, "Total Revenue", charts_dir / "07_scenario_forecast.png")

    # ── 5. Sensitivity Analysis ─────────────────────────────────
    print("\n[5/5] Running sensitivity analysis...")
    sensitivity = SensitivityAnalyzer(income_stmt)
    one_way = sensitivity.one_way_sensitivity()
    two_way = sensitivity.two_way_sensitivity()
    tornado = sensitivity.tornado_data()

    one_way.to_csv(reports_dir / f"{ticker}_sensitivity_oneway.csv", index=False)
    two_way.to_csv(reports_dir / f"{ticker}_sensitivity_twoway.csv")
    tornado.to_csv(reports_dir / f"{ticker}_tornado.csv", index=False)

    print("      Top sensitivity drivers:")
    for _, row in tornado.head(3).iterrows():
        print(f"        {row['Driver']}: range {pl.format_millions(row['Range'])}")

    viz.plot_tornado(tornado, charts_dir / "08_tornado_chart.png")
    viz.plot_sensitivity_heatmap(two_way, charts_dir / "09_sensitivity_heatmap.png")

    # ── Executive Summary Report ────────────────────────────────
    _write_executive_summary(
        reports_dir / f"{ticker}_executive_summary.txt",
        ticker, info, income_stmt, margins, growth, tornado, revenue_fc,
    )

    print(f"\n{'='*60}")
    print("  Analysis complete!")
    print(f"  Charts:  {charts_dir}")
    print(f"  Reports: {reports_dir}")
    print(f"{'='*60}\n")


def _write_executive_summary(
    path: Path,
    ticker: str,
    info: dict,
    income_stmt: pd.DataFrame,
    margins: pd.DataFrame,
    growth: pd.DataFrame,
    tornado: pd.DataFrame,
    forecast: pd.DataFrame,
) -> None:
    latest = income_stmt.index[-1]
    rev = income_stmt.loc[latest, "Total Revenue"]
    ni = income_stmt.loc[latest, "Net Income"]

    lines = [
        f"EXECUTIVE SUMMARY — {info['name']} ({ticker})",
        "=" * 55,
        "",
        f"Sector: {info['sector']} | Industry: {info['industry']}",
        f"Analysis Period: {income_stmt.index[0]}–{latest}",
        "",
        "KEY HIGHLIGHTS",
        "-" * 40,
        f"  Revenue ({latest}):     ${rev/1e9:.2f}B",
        f"  Net Income ({latest}):  ${ni/1e9:.2f}B",
    ]

    if not margins.empty and latest in margins.index:
        lines.append(f"  Net Margin:             {margins.loc[latest, 'Net Margin %']:.1f}%")
        lines.append(f"  Gross Margin:           {margins.loc[latest, 'Gross Margin %']:.1f}%")

    rev_growth_col = [c for c in growth.columns if "Total Revenue" in c]
    if rev_growth_col and latest in growth.index:
        g = growth.loc[latest, rev_growth_col[0]]
        if not pd.isna(g):
            lines.append(f"  Revenue YoY Growth:     {g:+.1f}%")

    lines.extend([
        "",
        "FORECAST",
        "-" * 40,
    ])
    fc = forecast[forecast["Type"] == "Forecast"]
    for yr, row in fc.iterrows():
        lines.append(f"  Revenue ({yr}):  ${row['Total Revenue']/1e9:.2f}B (forecast)")

    lines.extend([
        "",
        "SENSITIVITY — Top Drivers (±10%)",
        "-" * 40,
    ])
    for _, row in tornado.head(3).iterrows():
        lines.append(f"  {row['Driver']}: impact range ${row['Range']/1e9:.2f}B")

    lines.extend([
        "",
        "METHODOLOGY",
        "-" * 40,
        "  Data Source: Yahoo Finance API (yfinance)",
        "  P&L Analysis: Margin trends, YoY growth, expense breakdown",
        "  Budgeting: CAGR-based assumptions with variance analysis",
        "  Forecasting: Exponential smoothing + scenario modeling",
        "  Sensitivity: One-way, two-way tables & tornado chart",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_analysis()
