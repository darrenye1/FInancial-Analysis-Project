"""
Export full financial analysis workbook to Excel for learning.
Includes raw data + every analysis step with a guide sheet.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

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

DESKTOP_PATHS = [
    Path.home() / "Desktop",
    Path(r"f:\桌面"),
]


GUIDE_ROWS = [
    ["Tesla Financial Analysis — Excel Learning Workbook", ""],
    ["", ""],
    ["如何使用本文件", ""],
    ["1. 从 02–05 页查看 Yahoo Finance 原始三表 + 股价", ""],
    ["   格式：行 = 科目，列 = 年份（标准财报竖排展示）", ""],
    ["2. 从 06 页开始按 FP&A 分析流程逐步阅读", ""],
    ["3. 每个分析表对应项目 src/ 下的 Python 模块", ""],
    ["4. 21_Executive_Summary 为自动生成的文字结论", ""],
    ["", ""],
    ["分析流程 (Pipeline)", "对应模块"],
    ["Step 1: 数据获取", "src/data_fetcher.py → 02–05"],
    ["Step 2: P&L 分析", "src/pl_analysis.py → 06–09"],
    ["Step 3: 净利润 Bridge", "src/margin_bridge.py → 10"],
    ["Step 4: 现金流 & FCF", "src/cash_flow_analysis.py → 11"],
    ["Step 5: 营运资本 & CCC", "src/working_capital.py → 12"],
    ["Step 6: DuPont 回报率", "src/dupont_analysis.py → 13"],
    ["Step 7: 资本结构", "src/capital_structure.py → 14"],
    ["Step 8: 预算编制", "src/budgeting.py → 15"],
    ["Step 9: 预算差异", "src/budgeting.py → 16"],
    ["Step 10: 收入预测", "src/forecasting.py → 17–18"],
    ["Step 11: 敏感性分析", "src/sensitivity.py → 19–20"],
    ["Step 12: 管理层摘要", "src/executive_summary.py → 21"],
    ["", ""],
    ["关键 FP&A 公式速查", ""],
    ["毛利率", "= 毛利 / 营收"],
    ["净利率", "= 净利润 / 营收"],
    ["FCF", "= 经营现金流 - CapEx"],
    ["ROE (DuPont)", "= 净利率 × 资产周转率 × 权益乘数"],
    ["CCC", "= DSO + DIO - DPO"],
    ["预算差异 %", "= (实际 - 预算) / 预算"],
]


PIPELINE_ROWS = [
    ["Step", "Module", "Input Data", "Output Metrics", "FP&A Purpose"],
    [1, "data_fetcher", "Yahoo Finance API", "Income / BS / CF / Prices", "获取标准化财报数据"],
    [2, "pl_analysis", "Income Statement", "Margins, YoY Growth, Expense %", "盈利能力与费用结构"],
    [3, "margin_bridge", "Income Statement (2 years)", "Revenue/Margin/OpEx effects", "解释净利润变动原因"],
    [4, "cash_flow_analysis", "Cash Flow + Income", "OCF, FCF, OCF/NI", "盈利质量与流动性"],
    [5, "working_capital", "BS + Income", "DSO, DIO, DPO, CCC", "营运资本效率"],
    [6, "dupont_analysis", "BS + Income", "ROE, ROA, ROIC decomposition", "股东回报驱动因素"],
    [7, "capital_structure", "BS + Income", "Net Debt, Leverage, Coverage", "资本结构与偿债能力"],
    [8, "budgeting", "Historical Income", "Forward budget", "年度预算编制"],
    [9, "budgeting (variance)", "Budget vs Actual", "Variance %, Favorable/Unfavorable", "预算执行监控"],
    [10, "forecasting", "Historical Revenue", "Base forecast + Scenarios", "滚动预测与情景规划"],
    [11, "sensitivity", "Latest year actuals", "Tornado, One-way tables", "风险与驱动因素测试"],
    [12, "executive_summary", "All above", "Narrative report", "管理层汇报材料"],
]

INCOME_LINE_ORDER = [
    "Total Revenue", "Operating Revenue", "Cost Of Revenue", "Gross Profit",
    "Operating Expense", "Research And Development", "Selling General And Administration",
    "Operating Income", "EBITDA", "EBIT", "Interest Expense", "Interest Income",
    "Pretax Income", "Tax Provision", "Net Income", "Basic EPS", "Diluted EPS",
]


def _is_year_index(df: pd.DataFrame) -> bool:
    if df.empty:
        return False
    if df.index.name == "Year":
        return True
    try:
        return all(int(i) > 1900 for i in df.index)
    except (TypeError, ValueError):
        return False


def _vertical_format(df: pd.DataFrame, index_label: str = "Line Item") -> pd.DataFrame:
    """Standard financial statement layout: line items as rows, years as columns."""
    out = df.T.copy()
    out.index.name = index_label
    try:
        out = out.reindex(columns=sorted(out.columns, key=lambda x: int(x)))
    except (TypeError, ValueError):
        pass
    return out


def _order_line_items(df: pd.DataFrame, priority: list[str]) -> pd.DataFrame:
    idx = list(df.index)
    ordered = [k for k in priority if k in idx]
    ordered += sorted(k for k in idx if k not in ordered)
    return df.reindex(ordered)


def _write_df(
    writer: pd.ExcelWriter,
    sheet: str,
    df: pd.DataFrame,
    index: bool = True,
    vertical: bool = True,
    index_label: str = "Line Item",
    line_order: list[str] | None = None,
) -> None:
    name = sheet[:31]
    out = df.copy()
    if vertical and index and _is_year_index(out):
        out = _vertical_format(out, index_label=index_label)
        if line_order:
            out = _order_line_items(out, line_order)
        out.to_excel(writer, sheet_name=name, index=True)
    else:
        out.to_excel(writer, sheet_name=name, index=index)


def export_workbook(ticker: str = "TSLA", output_path: Path | None = None) -> Path:
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
    pl_summary = pl.summary_table()

    budget_analyzer = BudgetAnalyzer(income_stmt)
    base_year = income_stmt.index[-2]
    latest_year = income_stmt.index[-1]
    budget = budget_analyzer.create_budget(
        base_year=base_year,
        growth_assumptions={"Total Revenue": 0.12, "Operating Expense": 0.08},
        years_forward=2,
    )
    budget_summary = budget_analyzer.budget_summary(base_year=base_year, years_forward=2)
    variance = budget_analyzer.variance_analysis(budget, latest_year) if latest_year in budget.index else None

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
    wc_summary = WorkingCapitalAnalyzer(income_stmt, balance_sheet).summary()
    dupont = DuPontAnalyzer(income_stmt, balance_sheet).decompose()
    cap_struct = CapitalStructureAnalyzer(income_stmt, balance_sheet).summary()
    bridge = MarginBridgeAnalyzer(income_stmt).yoy_bridge()

    exec_summary = ExecutiveSummaryGenerator(
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
    ).generate()

    if output_path is None:
        stamp = datetime.now().strftime("%Y%m%d")
        for desktop in DESKTOP_PATHS:
            if desktop.exists():
                output_path = desktop / f"TSLA_Financial_Analysis_Workbook_{stamp}.xlsx"
                break
        else:
            output_path = ROOT / "outputs" / f"TSLA_Financial_Analysis_Workbook_{stamp}.xlsx"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    company_df = pd.DataFrame([info]).T
    company_df.columns = ["Value"]

    price_export = price_history.tail(252).reset_index()
    date_col = price_export.columns[0]
    price_export[date_col] = pd.to_datetime(price_export[date_col]).dt.tz_localize(None)
    price_export.rename(columns={date_col: "Date"}, inplace=True)

    summary_df = pd.DataFrame(exec_summary["sections"])

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame(GUIDE_ROWS, columns=["Topic", "Detail"]).to_excel(
            writer, sheet_name="00_Guide", index=False
        )
        pd.DataFrame(PIPELINE_ROWS[1:], columns=PIPELINE_ROWS[0]).to_excel(
            writer, sheet_name="00_Pipeline", index=False
        )
        company_df.to_excel(writer, sheet_name="01_Company_Info", index=True)

        _write_df(writer, "02_Income_Raw", income_stmt, line_order=INCOME_LINE_ORDER)
        _write_df(writer, "03_Balance_Raw", balance_sheet)
        _write_df(writer, "04_CashFlow_Raw", cash_flow)
        price_export.to_excel(writer, sheet_name="05_Price_1Y", index=False)

        key_pl = income_stmt[
            [c for c in ["Total Revenue", "Cost Of Revenue", "Gross Profit",
                         "Operating Expense", "Operating Income", "EBITDA", "Net Income"]
             if c in income_stmt.columns]
        ]
        _write_df(writer, "06_PL_Key_Lines", key_pl, index_label="Metric")
        _write_df(writer, "07_Margins", margins, index_label="Metric")
        _write_df(writer, "08_YoY_Growth", growth, index_label="Metric")
        _write_df(writer, "09_Expense_Pct", expense, index_label="Metric")
        _write_df(writer, "10_Margin_Bridge", bridge, index=False)

        _write_df(writer, "11_CashFlow_FCF", fcf_summary, index_label="Metric")
        _write_df(writer, "12_Working_Capital", wc_summary, index_label="Metric")
        _write_df(writer, "13_DuPont", dupont, index_label="Metric")
        _write_df(writer, "14_Capital_Structure", cap_struct, index_label="Metric")

        _write_df(writer, "15_Budget", budget, index_label="Metric")
        if variance is not None:
            variance.to_excel(writer, sheet_name="16_Variance", index=True)
        _write_df(writer, "16b_Budget_Summary", budget_summary, index_label="Metric")

        _write_df(writer, "17_Forecast", revenue_fc, index_label="Metric")
        _write_df(writer, "17b_Multi_Forecast", multi_fc, index_label="Metric")
        scenarios.to_excel(writer, sheet_name="18_Scenarios", index=False)

        one_way.to_excel(writer, sheet_name="19_Sensitivity_1Way", index=False)
        two_way.to_excel(writer, sheet_name="19b_Sensitivity_2Way")
        tornado.to_excel(writer, sheet_name="20_Tornado", index=False)

        summary_df.to_excel(writer, sheet_name="21_Executive_Summary", index=False)
        _write_df(writer, "22_PL_Full_Summary", pl_summary, index_label="Metric")

    print("Workbook saved:", output_path.name)
    # Also copy to alternate desktop if available
    for desktop in DESKTOP_PATHS:
        alt = desktop / output_path.name
        if desktop.exists() and alt.resolve() != output_path.resolve():
            import shutil
            shutil.copy(output_path, alt)
            print("Also copied to alternate desktop folder")
    return output_path


if __name__ == "__main__":
    path = export_workbook()
    print(str(path))
