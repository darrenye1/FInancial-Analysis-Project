"""YoY margin and profit bridge for FP&A reporting."""

from __future__ import annotations

import pandas as pd


class MarginBridgeAnalyzer:
    """Bridge net income change into revenue, margin, and opex effects."""

    def __init__(self, income_stmt: pd.DataFrame):
        self.income = income_stmt

    def yoy_bridge(self) -> pd.DataFrame:
        """Year-over-year profit bridge between consecutive years."""
        bridges = []
        years = sorted(self.income.index)

        for i in range(1, len(years)):
            curr, prev = years[i], years[i - 1]
            c, p = self.income.loc[curr], self.income.loc[prev]

            rev_c = self._val(c, "Total Revenue")
            rev_p = self._val(p, "Total Revenue")
            gp_c = self._val(c, "Gross Profit")
            gp_p = self._val(p, "Gross Profit")
            oi_c = self._val(c, "Operating Income")
            oi_p = self._val(p, "Operating Income")
            ni_c = self._val(c, "Net Income")
            ni_p = self._val(p, "Net Income")

            rev_effect = (rev_c - rev_p) * (gp_p / rev_p) if rev_p else 0
            margin_effect = rev_c * ((gp_c / rev_c) - (gp_p / rev_p)) if rev_c and rev_p else 0
            opex_effect = (oi_c - oi_p) - (gp_c - gp_p)
            other_effect = (ni_c - ni_p) - (oi_c - oi_p)

            bridges.append({
                "period": f"{prev} → {curr}",
                "toYear": int(curr),
                "Revenue Volume": round(rev_effect, 0),
                "Margin / Mix": round(margin_effect, 0),
                "OpEx Change": round(opex_effect, 0),
                "Below-the-Line": round(other_effect, 0),
                "Total Δ Net Income": round(ni_c - ni_p, 0),
            })

        return pd.DataFrame(bridges)

    @staticmethod
    def _val(series: pd.Series, key: str) -> float:
        if key not in series.index or pd.isna(series[key]):
            return 0.0
        return float(series[key])
