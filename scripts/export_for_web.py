"""Export analysis results as JSON for the Vercel web dashboard."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.budgeting import BudgetAnalyzer
from src.capital_structure import CapitalStructureAnalyzer
from src.cash_flow_analysis import CashFlowAnalyzer
from src.data_fetcher import FinancialDataFetcher
from src.dupont_analysis import DuPontAnalyzer
from src.executive_summary import ExecutiveSummaryGenerator
from src.forecasting import FinancialForecaster
from src.margin_bridge import MarginBridgeAnalyzer
from src.pl_analysis import PLAnalyzer
from src.sensitivity import SensitivityAnalyzer
from src.working_capital import WorkingCapitalAnalyzer


def _budget_summary_records(df: pd.DataFrame) -> list[dict]:
    """Budget summary with clear fiscal year + Actual/Budget labels."""
    records = []
    for fiscal_year, row in df.iterrows():
        entry = {
            "fiscalYear": int(fiscal_year),
            "Type": row.get("Type", "Actual"),
            "label": f"{int(fiscal_year)} {row.get('Type', 'Actual')}",
        }
        for col, val in row.items():
            if col == "Type":
                continue
            if pd.isna(val):
                entry[col] = None
            elif isinstance(val, (np.floating, float)):
                entry[col] = round(float(val), 2)
            else:
                entry[col] = val
        records.append(entry)
    return records


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for idx, row in df.iterrows():
        entry = {"year": int(idx) if isinstance(idx, (int, np.integer)) else str(idx)}
        for col, val in row.items():
            if pd.isna(val):
                entry[col] = None
            elif isinstance(val, (np.floating, float)):
                entry[col] = round(float(val), 2)
            else:
                entry[col] = val
        records.append(entry)
    return records


def _series_to_chart(df: pd.DataFrame, columns: list[str]) -> list[dict]:
    result = []
    for idx in df.index:
        point: dict = {"year": int(idx)}
        for col in columns:
            if col in df.columns and not pd.isna(df.loc[idx, col]):
                point[col] = round(float(df.loc[idx, col]), 2)
        result.append(point)
    return result


def export(ticker: str = "TSLA") -> Path:
    web_public = ROOT / "web" / "public"
    data_dir = web_public / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    fetcher = FinancialDataFetcher(ticker)
    info = fetcher.get_company_info()
    income_stmt = fetcher.get_income_statement()
    balance_sheet = fetcher.get_balance_sheet()
    cash_flow = fetcher.get_cash_flow()
    price_history = fetcher.get_price_history()

    pl = PLAnalyzer(income_stmt)
    margins = pl.margin_analysis()
    growth = pl.yoy_growth()
    expense = pl.expense_breakdown()

    budget_analyzer = BudgetAnalyzer(income_stmt)
    base_year = income_stmt.index[-2]
    latest_year = income_stmt.index[-1]
    budget = budget_analyzer.create_budget(
        base_year=base_year,
        growth_assumptions={"Total Revenue": 0.12, "Operating Expense": 0.08},
        years_forward=2,
    )
    budget_summary = budget_analyzer.budget_summary(
        base_year=base_year, years_forward=2, budget=budget
    )
    variance = None
    if latest_year in budget.index:
        variance = budget_analyzer.variance_analysis(budget, latest_year)

    forecaster = FinancialForecaster(income_stmt)
    revenue_fc = forecaster.forecast_metric("Total Revenue", periods=3)
    multi_fc = forecaster.multi_metric_forecast(periods=3)
    scenarios = forecaster.scenario_forecast("Total Revenue", periods=3)

    sensitivity = SensitivityAnalyzer(income_stmt)
    one_way = sensitivity.one_way_sensitivity()
    two_way = sensitivity.two_way_sensitivity()
    tornado = sensitivity.tornado_data()

    cf_analyzer = CashFlowAnalyzer(income_stmt, cash_flow, balance_sheet)
    fcf_summary = cf_analyzer.fcf_summary()
    wc_analyzer = WorkingCapitalAnalyzer(income_stmt, balance_sheet)
    wc_summary = wc_analyzer.summary()
    dupont = DuPontAnalyzer(income_stmt, balance_sheet).decompose()
    cap_struct = CapitalStructureAnalyzer(income_stmt, balance_sheet).summary()
    bridge = MarginBridgeAnalyzer(income_stmt).yoy_bridge()

    summary_gen = ExecutiveSummaryGenerator(
        ticker=ticker,
        company_name=info["name"],
        income_stmt=income_stmt,
        margins=margins,
        growth=growth,
        fcf_summary=fcf_summary,
        wc_summary=wc_summary,
        dupont=dupont,
        cap_struct=cap_struct,
        variance=variance,
        bridge=bridge,
        tornado=tornado,
        revenue_fc=revenue_fc,
        scenarios=scenarios,
    )
    executive_summary = summary_gen.generate()

    latest = int(latest_year)
    rev = float(income_stmt.loc[latest_year, "Total Revenue"])
    ni = float(income_stmt.loc[latest_year, "Net Income"])

    latest_fcf = float(fcf_summary.loc[latest_year, "Free Cash Flow"]) if latest_year in fcf_summary.index else None
    latest_roe = float(dupont.loc[latest_year, "ROE %"]) if latest_year in dupont.index else None
    latest_ccc = float(wc_summary.loc[latest_year, "Cash Conversion Cycle"]) if latest_year in wc_summary.index and not pd.isna(wc_summary.loc[latest_year, "Cash Conversion Cycle"]) else None

    payload = {
        "ticker": ticker,
        "company": {
            "name": info["name"],
            "sector": info["sector"],
            "industry": info["industry"],
            "employees": info["employees"],
            "marketCap": info["market_cap"],
            "currency": info["currency"],
        },
        "highlights": {
            "latestYear": latest,
            "revenue": round(rev, 0),
            "netIncome": round(ni, 0),
            "netMargin": round(float(margins.loc[latest_year, "Net Margin %"]), 2) if latest in margins.index else None,
            "grossMargin": round(float(margins.loc[latest_year, "Gross Margin %"]), 2) if latest in margins.index else None,
            "revenueYoY": round(float(growth.loc[latest_year, "Total Revenue YoY %"]), 2)
            if "Total Revenue YoY %" in growth.columns and latest in growth.index and not pd.isna(growth.loc[latest_year, "Total Revenue YoY %"])
            else None,
            "freeCashFlow": round(latest_fcf, 0) if latest_fcf is not None else None,
            "roe": latest_roe,
            "cashConversionCycle": latest_ccc,
        },
        "pl": {
            "incomeStatement": _series_to_chart(
                income_stmt,
                ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"],
            ),
            "margins": _df_to_records(margins),
            "growth": _df_to_records(growth),
            "expenseBreakdown": _df_to_records(expense),
        },
        "budget": {
            "summary": _budget_summary_records(budget_summary),
            "variance": variance.reset_index().to_dict(orient="records") if variance is not None else [],
        },
        "forecast": {
            "revenue": _df_to_records(revenue_fc),
            "multiMetric": _df_to_records(multi_fc),
            "scenarios": scenarios.to_dict(orient="records"),
        },
        "sensitivity": {
            "oneWay": one_way.to_dict(orient="records"),
            "twoWay": {
                "columns": [str(c) for c in two_way.columns],
                "rows": [
                    {"change": str(idx), **{str(c): round(float(v), 0) if not pd.isna(v) else None for c, v in row.items()}}
                    for idx, row in two_way.iterrows()
                ],
            },
            "tornado": tornado.to_dict(orient="records"),
        },
        "corpFin": {
            "cashFlow": _df_to_records(fcf_summary),
            "workingCapital": _df_to_records(wc_summary),
            "dupont": _df_to_records(dupont),
            "capitalStructure": _df_to_records(cap_struct),
            "marginBridge": bridge.to_dict(orient="records"),
        },
        "summary": executive_summary,
        "stockPrice": [
            {
                "date": d.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            }
            for d, row in price_history.tail(252).iterrows()
        ],
        "generatedAt": pd.Timestamp.now().isoformat(),
    }

    out_path = data_dir / "analysis.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Copy to web import path for Next.js build
    web_data = ROOT / "web" / "data" / "analysis.json"
    web_data.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(out_path, web_data)

    print("Exported:", out_path.name)
    return out_path


if __name__ == "__main__":
    export()
