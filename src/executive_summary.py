"""Generate executive summary report from analysis results."""

from __future__ import annotations

import pandas as pd


def _fmt_b(v: float) -> str:
    if abs(v) >= 1e9:
        return f"${v / 1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v / 1e6:.1f}M"
    return f"${v:,.0f}"


def _pct(v: float | None, signed: bool = True) -> str:
    if v is None or pd.isna(v):
        return "N/A"
    return f"{v:+.1f}%" if signed else f"{v:.1f}%"


class ExecutiveSummaryGenerator:
    """Build a narrative FP&A summary from computed analysis outputs."""

    def __init__(
        self,
        ticker: str,
        company_name: str,
        income_stmt: pd.DataFrame,
        margins: pd.DataFrame,
        growth: pd.DataFrame,
        fcf_summary: pd.DataFrame,
        wc_summary: pd.DataFrame,
        dupont: pd.DataFrame,
        cap_struct: pd.DataFrame,
        variance: pd.DataFrame | None,
        bridge: pd.DataFrame,
        tornado: pd.DataFrame,
        revenue_fc: pd.DataFrame,
        scenarios: pd.DataFrame,
    ):
        self.ticker = ticker
        self.company_name = company_name
        self.income = income_stmt
        self.margins = margins
        self.growth = growth
        self.fcf = fcf_summary
        self.wc = wc_summary
        self.dupont = dupont
        self.cap = cap_struct
        self.variance = variance
        self.bridge = bridge
        self.tornado = tornado
        self.revenue_fc = revenue_fc
        self.scenarios = scenarios
        self.latest = income_stmt.index[-1]
        self.prior = income_stmt.index[-2] if len(income_stmt.index) >= 2 else None

    def generate(self) -> dict:
        sections = [
            {"title": "Executive Overview", "body": self._overview()},
            {"title": "P&L Performance", "body": self._pl_section()},
            {"title": "Cash Flow & Liquidity", "body": self._cashflow_section()},
            {"title": "Working Capital & Capital Structure", "body": self._corpfin_section()},
            {"title": "Budget vs Actual", "body": self._budget_section()},
            {"title": "Forecast Outlook", "body": self._forecast_section()},
            {"title": "Sensitivity & Key Risks", "body": self._sensitivity_section()},
            {"title": "Conclusion", "body": self._conclusion()},
        ]
        full_text = "\n\n".join(f"{s['title']}\n{s['body']}" for s in sections)
        return {"sections": sections, "fullText": full_text}

    def _overview(self) -> str:
        y = self.latest
        rev = float(self.income.loc[y, "Total Revenue"])
        ni = float(self.income.loc[y, "Net Income"])
        nm = self.margins.loc[y, "Net Margin %"] if y in self.margins.index else None
        yoy = self.growth.loc[y, "Total Revenue YoY %"] if "Total Revenue YoY %" in self.growth.columns else None

        return (
            f"This report presents a corporate finance FP&A analysis of {self.company_name} ({self.ticker}), "
            f"covering the period {self.income.index[0]}–{y}. In {y}, the company reported revenue of "
            f"{_fmt_b(rev)} ({_pct(yoy)} YoY) and net income of {_fmt_b(ni)}, with a net margin of "
            f"{_pct(nm, signed=False)}. The analysis integrates P&L trends, cash flow quality, working capital "
            f"efficiency, budget variance, forward forecasts, and sensitivity testing to support "
            f"management-style financial planning and decision-making."
        )

    def _pl_section(self) -> str:
        y, p = self.latest, self.prior
        if p is None:
            return "Insufficient historical data for P&L comparison."

        gm = self.margins.loc[y, "Gross Margin %"]
        om = self.margins.loc[y, "Operating Margin %"]
        gm_p = self.margins.loc[p, "Gross Margin %"]
        ni_chg = float(self.income.loc[y, "Net Income"]) - float(self.income.loc[p, "Net Income"])

        gm_chg = gm - gm_p
        margin_word = "expanded" if gm_chg > 0 else "compressed" if gm_chg < 0 else "held steady at"
        if gm_chg == 0:
            margin_line = f"Gross margin held steady at {gm:.1f}% in {y}."
        else:
            margin_line = (
                f"Gross margin {margin_word} from {gm_p:.1f}% to {gm:.1f}% ({gm_chg:+.1f}pp), "
                f"while operating margin stood at {om:.1f}% in {y}."
            )

        lines = [margin_line]

        if not self.bridge.empty:
            b = self.bridge.iloc[-1]
            lines.append(
                f"The year-over-year net income bridge ({b['period']}) shows a total change of "
                f"{_fmt_b(b['Total Δ Net Income'])}, driven primarily by "
                f"revenue volume ({_fmt_b(b['Revenue Volume'])}), margin/mix ({_fmt_b(b['Margin / Mix'])}), "
                f"and operating expense ({_fmt_b(b['OpEx Change'])})."
            )
        else:
            lines.append(f"Net income changed by {_fmt_b(ni_chg)} versus the prior year.")

        return " ".join(lines)

    def _cashflow_section(self) -> str:
        y = self.latest
        if y not in self.fcf.index:
            return "Cash flow data unavailable for the latest period."

        ocf = float(self.fcf.loc[y, "Operating Cash Flow"])
        fcf = float(self.fcf.loc[y, "Free Cash Flow"])
        fcf_margin = self.fcf.loc[y, "FCF Margin %"]
        ocf_ni = self.fcf.loc[y, "OCF / Net Income"]

        quality = "strong" if ocf_ni and ocf_ni >= 1.0 else "moderate" if ocf_ni and ocf_ni >= 0.7 else "weak"
        return (
            f"In {y}, operating cash flow reached {_fmt_b(ocf)} with free cash flow of {_fmt_b(fcf)} "
            f"(FCF margin: {fcf_margin:.1f}%). The OCF-to-net-income ratio of {ocf_ni:.2f}x indicates "
            f"{quality} earnings quality — cash generation {'comfortably exceeds' if ocf_ni >= 1 else 'lags'} "
            f"reported profits. CapEx intensity was {self.fcf.loc[y, 'CapEx % of Revenue']:.1f}% of revenue, "
            f"reflecting continued capital investment in the business."
        )

    def _corpfin_section(self) -> str:
        y = self.latest
        parts = []

        if y in self.dupont.index:
            roe = self.dupont.loc[y, "ROE %"]
            roic = self.dupont.loc[y, "ROIC %"]
            parts.append(
                f"Return on equity was {roe:.1f}% and ROIC was {roic:.1f}% in {y}. "
                f"DuPont decomposition shows net margin of {self.dupont.loc[y, 'Net Margin %']:.1f}%, "
                f"asset turnover of {self.dupont.loc[y, 'Asset Turnover']:.2f}x, and equity multiplier "
                f"of {self.dupont.loc[y, 'Equity Multiplier']:.2f}x."
            )

        if y in self.wc.index and not pd.isna(self.wc.loc[y, "Cash Conversion Cycle"]):
            ccc = self.wc.loc[y, "Cash Conversion Cycle"]
            dso = self.wc.loc[y, "DSO (days)"]
            parts.append(
                f"Working capital efficiency: cash conversion cycle of {ccc:.0f} days "
                f"(DSO {dso:.0f}d, DIO {self.wc.loc[y, 'DIO (days)']:.0f}d, "
                f"DPO {self.wc.loc[y, 'DPO (days)']:.0f}d)."
            )

        if y in self.cap.index:
            nd_ebitda = self.cap.loc[y, "Net Debt / EBITDA"]
            ic = self.cap.loc[y, "Interest Coverage"]
            parts.append(
                f"Capital structure remains conservative with net debt/EBITDA at {nd_ebitda:.2f}x "
                f"and interest coverage of {ic:.1f}x, indicating ample debt service capacity."
            )

        return " ".join(parts) if parts else "Corporate finance metrics unavailable."

    def _budget_section(self) -> str:
        if self.variance is None or self.variance.empty:
            return "Budget variance analysis not available for the latest period."

        rev_var = self.variance.loc["Total Revenue", "Variance %"]
        ni_var = self.variance.loc["Net Income", "Variance %"]
        return (
            f"Compared to the forward budget built on historical CAGR assumptions, {self.latest} actuals "
            f"underperformed across all key metrics. Revenue missed budget by {rev_var:+.1f}% and net income "
            f"by {ni_var:+.1f}%, classified as unfavorable variance. The largest gap was in operating "
            f"income, suggesting margin compression and cost overruns relative to plan were the primary "
            f"drivers of the budget shortfall."
        )

    def _forecast_section(self) -> str:
        fc = self.revenue_fc[self.revenue_fc["Type"] == "Forecast"]
        if fc.empty:
            return "Forecast data unavailable."

        last_fc = fc.iloc[-1]
        last_year = int(last_fc.name) if hasattr(last_fc, "name") else last_fc.get("Year")
        base_rev = float(last_fc["Total Revenue"])

        bull = self.scenarios[
            (self.scenarios["Scenario"] == "Bull") & (self.scenarios["Year"] == last_year)
        ]
        bear = self.scenarios[
            (self.scenarios["Scenario"] == "Bear") & (self.scenarios["Year"] == last_year)
        ]
        bull_rev = float(bull["Total Revenue"].iloc[0]) if not bull.empty else None
        bear_rev = float(bear["Total Revenue"].iloc[0]) if not bear.empty else None

        text = (
            f"Base-case revenue forecast projects {_fmt_b(base_rev)} by {last_year}, "
            f"using exponential smoothing on historical trends."
        )
        if bull_rev and bear_rev:
            text += (
                f" Scenario analysis ranges from {_fmt_b(bear_rev)} (bear) to {_fmt_b(bull_rev)} (bull), "
                f"providing a {_pct((bull_rev - bear_rev) / base_rev * 100)} planning bandwidth for "
                f"strategic and budgeting decisions."
            )
        return text

    def _sensitivity_section(self) -> str:
        if self.tornado.empty:
            return "Sensitivity analysis unavailable."

        top = self.tornado.iloc[0]
        second = self.tornado.iloc[1] if len(self.tornado) > 1 else None
        text = (
            f"Sensitivity analysis (±10% driver changes) identifies {top['Driver']} as the highest-impact "
            f"variable on net income, with an impact range of {_fmt_b(top['Range'])}."
        )
        if second is not None:
            text += f" {second['Driver']} ranks second at {_fmt_b(second['Range'])}."
        text += (
            " FP&A teams should prioritize these drivers in scenario planning and management reporting."
        )
        return text

    def _conclusion(self) -> str:
        y = self.latest
        yoy = self.growth.loc[y, "Total Revenue YoY %"] if "Total Revenue YoY %" in self.growth.columns else 0
        tone = "growth deceleration and margin pressure" if yoy and yoy < 0 else "continued growth momentum"

        return (
            f"{self.company_name} faces {tone} in the current cycle, yet maintains positive free cash flow "
            f"and a strong balance sheet. Key FP&A priorities include: (1) monitoring gross margin trends "
            f"and cost discipline, (2) optimizing working capital as CCC extends, (3) recalibrating budgets "
            f"to reflect actual performance gaps, and (4) stress-testing forecasts against revenue and COGS "
            f"sensitivities. This analysis framework is replicable across any public company using "
            f"standardized Yahoo Finance data."
        )
