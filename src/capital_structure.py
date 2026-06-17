"""Capital structure and leverage metrics for corporate finance FP&A."""

from __future__ import annotations

import pandas as pd


class CapitalStructureAnalyzer:
    """Net debt, leverage ratios, and interest coverage."""

    def __init__(
        self,
        income_stmt: pd.DataFrame,
        balance_sheet: pd.DataFrame,
    ):
        self.income = income_stmt
        self.bs = balance_sheet

    def summary(self) -> pd.DataFrame:
        rows = []
        years = sorted(set(self.income.index) & set(self.bs.index))

        for year in years:
            inc = self.income.loc[year]
            bs = self.bs.loc[year]

            total_debt = self._val(bs, "Total Debt")
            cash = self._val(bs, "Cash And Cash Equivalents") or self._val(
                bs, "Cash Cash Equivalents And Short Term Investments"
            )
            equity = self._val(bs, "Stockholders Equity") or self._val(bs, "Common Stock Equity")
            ebitda = self._val(inc, "EBITDA")
            ebit = self._val(inc, "Operating Income")
            interest = abs(self._val(inc, "Interest Expense"))

            net_debt = total_debt - cash
            net_debt_ebitda = net_debt / ebitda if ebitda else None
            debt_equity = total_debt / equity if equity else None
            interest_coverage = ebit / interest if interest else None

            rows.append({
                "Total Debt": total_debt,
                "Net Debt": net_debt,
                "Cash": cash,
                "Debt / Equity": round(debt_equity, 2) if debt_equity is not None else None,
                "Net Debt / EBITDA": round(net_debt_ebitda, 2) if net_debt_ebitda is not None else None,
                "Interest Coverage": round(interest_coverage, 2) if interest_coverage is not None else None,
            })

        return pd.DataFrame(rows, index=years)

    @staticmethod
    def _val(series: pd.Series, key: str) -> float:
        if key not in series.index or pd.isna(series[key]):
            return 0.0
        return float(series[key])
