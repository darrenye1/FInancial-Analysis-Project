"""Budget planning and variance analysis."""

from __future__ import annotations

import pandas as pd


class BudgetAnalyzer:
    """
    Build a forward-looking budget from historical trends and compare
  against actuals (variance analysis).
    """

    def __init__(self, income_stmt: pd.DataFrame):
        self.income_stmt = income_stmt

    def create_budget(
        self,
        base_year: int,
        growth_assumptions: dict[str, float] | None = None,
        years_forward: int = 2,
    ) -> pd.DataFrame:
        """
        Create a budget projection from base-year actuals.

        growth_assumptions: e.g. {"Total Revenue": 0.15, "Operating Expense": 0.10}
        """
        if base_year not in self.income_stmt.index:
            raise ValueError(f"Base year {base_year} not in data")

        base = self.income_stmt.loc[base_year]
        defaults = self._infer_growth_rates()
        assumptions = {**defaults, **(growth_assumptions or {})}

        budget_rows = []
        for yr in range(1, years_forward + 1):
            year = base_year + yr
            row = {"Year": year, "Type": "Budget"}
            for metric in ["Total Revenue", "Cost Of Revenue", "Operating Expense"]:
                if metric in base.index:
                    rate = assumptions.get(metric, 0.05)
                    row[metric] = base[metric] * (1 + rate) ** yr
            if "Total Revenue" in row and "Cost Of Revenue" in row:
                row["Gross Profit"] = row["Total Revenue"] - row["Cost Of Revenue"]
            if all(k in row for k in ["Gross Profit", "Operating Expense"]):
                row["Operating Income"] = row["Gross Profit"] - row["Operating Expense"]
                row["Net Income"] = row["Operating Income"] * 0.75
            budget_rows.append(row)

        return pd.DataFrame(budget_rows).set_index("Year")

    def _infer_growth_rates(self) -> dict[str, float]:
        """Use trailing 3-year CAGR as default growth assumptions."""
        rates = {}
        for metric in ["Total Revenue", "Cost Of Revenue", "Operating Expense"]:
            if metric not in self.income_stmt.columns:
                continue
            series = self.income_stmt[metric].dropna()
            if len(series) >= 2:
                n = len(series) - 1
                cagr = (series.iloc[-1] / series.iloc[0]) ** (1 / n) - 1
                rates[metric] = round(cagr, 4)
            else:
                rates[metric] = 0.05
        return rates

    def variance_analysis(
        self,
        budget: pd.DataFrame,
        actual_year: int,
    ) -> pd.DataFrame:
        """Compare budget vs actual for a given year."""
        if actual_year not in self.income_stmt.index:
            raise ValueError(f"Actual year {actual_year} not in data")
        if actual_year not in budget.index:
            raise ValueError(f"Year {actual_year} not in budget")

        actual = self.income_stmt.loc[actual_year]
        planned = budget.loc[actual_year]

        metrics = [
            m for m in ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
            if m in actual.index and m in planned.index
        ]

        rows = []
        for m in metrics:
            act, bud = actual[m], planned[m]
            var = act - bud
            var_pct = (var / bud * 100) if bud != 0 else 0
            rows.append({
                "Metric": m,
                "Budget": bud,
                "Actual": act,
                "Variance": var,
                "Variance %": round(var_pct, 2),
                "Status": "Favorable" if var >= 0 else "Unfavorable",
            })
        return pd.DataFrame(rows).set_index("Metric")

    def budget_summary(self, base_year: int, years_forward: int = 2) -> pd.DataFrame:
        """Combine historical actuals with forward budget."""
        budget = self.create_budget(base_year, years_forward=years_forward)
        hist = self.income_stmt[
            [c for c in ["Total Revenue", "Cost Of Revenue", "Gross Profit",
                         "Operating Income", "Net Income"]
             if c in self.income_stmt.columns]
        ].copy()
        hist["Type"] = "Actual"
        budget = budget[[c for c in hist.columns if c in budget.columns]]
        combined = pd.concat([hist, budget])
        return combined.sort_index()
