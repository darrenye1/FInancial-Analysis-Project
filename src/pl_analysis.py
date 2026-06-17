"""Profit & Loss (Income Statement) analysis."""

from __future__ import annotations

import pandas as pd


class PLAnalyzer:
    """Analyze revenue, margins, and profitability trends."""

    KEY_METRICS = [
        "Total Revenue",
        "Cost Of Revenue",
        "Gross Profit",
        "Operating Expense",
        "Operating Income",
        "Net Income",
        "EBITDA",
        "Basic EPS",
        "Diluted EPS",
    ]

    def __init__(self, income_stmt: pd.DataFrame):
        self.income_stmt = income_stmt
        self.metrics = self._extract_metrics()

    def _extract_metrics(self) -> pd.DataFrame:
        available = [m for m in self.KEY_METRICS if m in self.income_stmt.columns]
        return self.income_stmt[available].copy()

    def margin_analysis(self) -> pd.DataFrame:
        df = self.metrics.copy()
        revenue = df.get("Total Revenue")
        if revenue is None:
            return pd.DataFrame()

        margins = pd.DataFrame(index=df.index)
        margins["Gross Margin %"] = (df["Gross Profit"] / revenue * 100).round(2)
        margins["Operating Margin %"] = (df["Operating Income"] / revenue * 100).round(2)
        margins["Net Margin %"] = (df["Net Income"] / revenue * 100).round(2)
        if "EBITDA" in df.columns:
            margins["EBITDA Margin %"] = (df["EBITDA"] / revenue * 100).round(2)
        return margins

    def yoy_growth(self) -> pd.DataFrame:
        df = self.metrics.copy()
        growth = df.pct_change() * 100
        growth.columns = [f"{c} YoY %" for c in growth.columns]
        return growth.round(2)

    def expense_breakdown(self) -> pd.DataFrame:
        df = self.metrics.copy()
        revenue = df.get("Total Revenue")
        if revenue is None:
            return pd.DataFrame()

        breakdown = pd.DataFrame(index=df.index)
        if "Cost Of Revenue" in df.columns:
            breakdown["COGS % of Revenue"] = (df["Cost Of Revenue"] / revenue * 100).round(2)
        if "Operating Expense" in df.columns:
            breakdown["OpEx % of Revenue"] = (df["Operating Expense"] / revenue * 100).round(2)
        if "Research And Development" in self.income_stmt.columns:
            rd = self.income_stmt["Research And Development"]
            breakdown["R&D % of Revenue"] = (rd / revenue * 100).round(2)
        if "Selling General And Administration" in self.income_stmt.columns:
            sga = self.income_stmt["Selling General And Administration"]
            breakdown["SG&A % of Revenue"] = (sga / revenue * 100).round(2)
        return breakdown

    def summary_table(self) -> pd.DataFrame:
        """Consolidated P&L summary with growth and margins."""
        summary = self.metrics.copy()
        growth = self.yoy_growth()
        margins = self.margin_analysis()

        for col in growth.columns:
            summary[col] = growth[col]
        for col in margins.columns:
            summary[col] = margins[col]
        return summary

    @staticmethod
    def format_millions(value: float) -> str:
        if pd.isna(value):
            return "N/A"
        if abs(value) >= 1e9:
            return f"${value / 1e9:.2f}B"
        return f"${value / 1e6:.1f}M"
