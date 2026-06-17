"""DuPont ROE decomposition and return metrics."""

from __future__ import annotations

import pandas as pd


class DuPontAnalyzer:
    """
    DuPont 3-factor: ROE = Net Margin × Asset Turnover × Equity Multiplier
    Plus ROA and ROIC proxies for corp fin FP&A.
    """

    def __init__(
        self,
        income_stmt: pd.DataFrame,
        balance_sheet: pd.DataFrame,
    ):
        self.income = income_stmt
        self.bs = balance_sheet

    def decompose(self) -> pd.DataFrame:
        rows = []
        years = sorted(set(self.income.index) & set(self.bs.index))

        for year in years:
            inc = self.income.loc[year]
            bs = self.bs.loc[year]

            revenue = self._val(inc, "Total Revenue")
            net_income = self._val(inc, "Net Income")
            ebit = self._val(inc, "Operating Income")
            total_assets = self._val(bs, "Total Assets")
            equity = self._val(bs, "Stockholders Equity") or self._val(bs, "Common Stock Equity")
            invested = self._val(bs, "Invested Capital")

            net_margin = net_income / revenue if revenue else 0
            asset_turnover = revenue / total_assets if total_assets else 0
            equity_multiplier = total_assets / equity if equity else 0
            roe = net_margin * asset_turnover * equity_multiplier
            roa = net_income / total_assets if total_assets else 0
            roic = ebit / invested if invested else 0

            rows.append({
                "ROE %": round(roe * 100, 2),
                "ROA %": round(roa * 100, 2),
                "ROIC %": round(roic * 100, 2),
                "Net Margin %": round(net_margin * 100, 2),
                "Asset Turnover": round(asset_turnover, 2),
                "Equity Multiplier": round(equity_multiplier, 2),
            })

        return pd.DataFrame(rows, index=years)

    @staticmethod
    def _val(series: pd.Series, key: str) -> float:
        if key not in series.index or pd.isna(series[key]):
            return 0.0
        return float(series[key])
