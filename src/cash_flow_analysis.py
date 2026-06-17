"""Cash flow and free cash flow analysis for FP&A."""

from __future__ import annotations

import pandas as pd


class CashFlowAnalyzer:
    """Analyze operating cash flow, FCF, and cash conversion quality."""

    def __init__(
        self,
        income_stmt: pd.DataFrame,
        cash_flow: pd.DataFrame,
        balance_sheet: pd.DataFrame | None = None,
    ):
        self.income = income_stmt
        self.cash_flow = cash_flow
        self.balance_sheet = balance_sheet

    def fcf_summary(self) -> pd.DataFrame:
        """OCF, CapEx, FCF and key FP&A ratios."""
        rows = []
        for year in self.cash_flow.index:
            cf = self.cash_flow.loc[year]
            inc = self.income.loc[year] if year in self.income.index else pd.Series(dtype=float)

            ocf = self._val(cf, "Operating Cash Flow")
            capex = abs(self._val(cf, "Capital Expenditure"))
            fcf = self._val(cf, "Free Cash Flow")
            if fcf == 0 and ocf:
                fcf = ocf - capex

            revenue = self._val(inc, "Total Revenue")
            net_income = self._val(inc, "Net Income")

            rows.append({
                "Operating Cash Flow": ocf,
                "Capital Expenditure": capex,
                "Free Cash Flow": fcf,
                "FCF Margin %": round(fcf / revenue * 100, 2) if revenue else None,
                "CapEx % of Revenue": round(capex / revenue * 100, 2) if revenue else None,
                "OCF / Net Income": round(ocf / net_income, 2) if net_income else None,
            })

        return pd.DataFrame(rows, index=self.cash_flow.index)

    def cash_conversion(self) -> pd.DataFrame:
        """Cash conversion metrics — earnings quality check."""
        summary = self.fcf_summary()
        result = pd.DataFrame(index=summary.index)
        result["OCF / Net Income"] = summary["OCF / Net Income"]
        result["FCF Margin %"] = summary["FCF Margin %"]
        result["CapEx % of Revenue"] = summary["CapEx % of Revenue"]
        return result

    @staticmethod
    def _val(series: pd.Series, key: str) -> float:
        if key not in series.index or pd.isna(series[key]):
            return 0.0
        return float(series[key])
