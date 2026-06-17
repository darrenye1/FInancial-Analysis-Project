"""Working capital and cash conversion cycle analysis."""

from __future__ import annotations

import pandas as pd


class WorkingCapitalAnalyzer:
    """FP&A working capital metrics and cash conversion cycle."""

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

        for i, year in enumerate(years):
            inc = self.income.loc[year]
            bs = self.bs.loc[year]
            prev_year = years[i - 1] if i > 0 else None

            revenue = self._val(inc, "Total Revenue")
            cogs = self._val(inc, "Cost Of Revenue")
            wc = self._val(bs, "Working Capital")

            ar = self._val(bs, "Accounts Receivable")
            inv = self._val(bs, "Inventory")
            ap = self._val(bs, "Accounts Payable")

            dso = round(ar / revenue * 365, 1) if revenue else None
            dio = round(inv / cogs * 365, 1) if cogs else None
            dpo = round(ap / cogs * 365, 1) if cogs else None
            ccc = round((dso or 0) + (dio or 0) - (dpo or 0), 1) if any([dso, dio, dpo]) else None

            delta_wc = None
            if prev_year and prev_year in self.bs.index:
                prev_wc = self._val(self.bs.loc[prev_year], "Working Capital")
                delta_wc = wc - prev_wc

            rows.append({
                "Working Capital": wc,
                "WC % of Revenue": round(wc / revenue * 100, 2) if revenue else None,
                "Δ Working Capital": delta_wc,
                "DSO (days)": dso,
                "DIO (days)": dio,
                "DPO (days)": dpo,
                "Cash Conversion Cycle": ccc,
            })

        return pd.DataFrame(rows, index=years)

    @staticmethod
    def _val(series: pd.Series, key: str) -> float:
        if key not in series.index or pd.isna(series[key]):
            return 0.0
        return float(series[key])
