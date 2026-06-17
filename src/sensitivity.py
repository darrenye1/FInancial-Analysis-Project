"""Sensitivity and scenario analysis."""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd


class SensitivityAnalyzer:
    """One-way and two-way sensitivity tables for key drivers."""

    def __init__(self, income_stmt: pd.DataFrame):
        self.income_stmt = income_stmt
        self.base_year = income_stmt.index[-1]
        self.base = income_stmt.loc[self.base_year]

    def one_way_sensitivity(
        self,
        driver: str = "Total Revenue",
        driver_changes: list[float] | None = None,
        target: str = "Net Income",
    ) -> pd.DataFrame:
        driver_changes = driver_changes or [-0.20, -0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15, 0.20]
        base_driver = self.base.get(driver, 0)
        base_target = self._compute_target(target, self.base)

        rows = []
        for pct in driver_changes:
            adjusted = self._adjust_driver(driver, pct)
            new_target = self._compute_target(target, adjusted)
            impact = new_target - base_target
            rows.append({
                f"{driver} Change %": pct * 100,
                f"Base {driver}": base_driver,
                f"Adjusted {driver}": adjusted[driver],
                f"Base {target}": base_target,
                f"Adjusted {target}": new_target,
                f"{target} Impact": impact,
                f"{target} Impact %": (impact / base_target * 100) if base_target else 0,
            })
        return pd.DataFrame(rows)

    def _adjust_driver(self, driver: str, pct_change: float) -> pd.Series:
        """Adjust a driver and cascade impact to dependent line items."""
        adjusted = self.base.copy()
        adjusted[driver] = self.base[driver] * (1 + pct_change)

        if driver == "Total Revenue":
            base_rev = self.base.get("Total Revenue", 1)
            ratio = adjusted["Total Revenue"] / base_rev if base_rev else 1
            if "Cost Of Revenue" in adjusted.index:
                adjusted["Cost Of Revenue"] = self.base["Cost Of Revenue"] * ratio
            if "Gross Profit" in adjusted.index:
                adjusted["Gross Profit"] = adjusted["Total Revenue"] - adjusted.get("Cost Of Revenue", 0)
        elif driver == "Cost Of Revenue":
            if "Gross Profit" in adjusted.index:
                adjusted["Gross Profit"] = adjusted.get("Total Revenue", 0) - adjusted["Cost Of Revenue"]
        elif driver == "Operating Expense":
            pass

        if "Gross Profit" in adjusted.index and "Operating Expense" in adjusted.index:
            adjusted["Operating Income"] = adjusted["Gross Profit"] - adjusted["Operating Expense"]

        return adjusted

    def two_way_sensitivity(
        self,
        driver_x: str = "Total Revenue",
        driver_y: str = "Operating Expense",
        changes: list[float] | None = None,
        target: str = "Net Income",
    ) -> pd.DataFrame:
        """Two-way sensitivity table (data table)."""
        changes = changes or [-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15]
        base_x = self.base.get(driver_x, 0)
        base_y = self.base.get(driver_y, 0)
        base_target = self._compute_target(target, self.base)

        table = pd.DataFrame(index=[f"{c*100:+.0f}%" for c in changes])
        table.index.name = f"{driver_y} Change"

        for cx in changes:
            col_vals = []
            for cy in changes:
                adjusted = self._adjust_driver(driver_x, cx)
                base_y = self.base.get(driver_y, 0)
                adjusted[driver_y] = base_y * (1 + cy)
                if driver_y == "Operating Expense" and "Gross Profit" in adjusted.index:
                    adjusted["Operating Income"] = adjusted["Gross Profit"] - adjusted["Operating Expense"]
                new_target = self._compute_target(target, adjusted)
                col_vals.append(new_target)
            table[f"{driver_x} {cx*100:+.0f}%"] = col_vals

        table.columns.name = driver_x
        return table

    def margin_sensitivity(
        self,
        revenue_changes: list[float] | None = None,
        margin_changes: list[float] | None = None,
    ) -> pd.DataFrame:
        """Sensitivity of net income to revenue and gross margin changes."""
        revenue_changes = revenue_changes or [-0.20, -0.10, 0, 0.10, 0.20]
        margin_changes = margin_changes or [-5, -2.5, 0, 2.5, 5]

        base_revenue = self.base.get("Total Revenue", 0)
        base_gp = self.base.get("Gross Profit", 0)
        base_margin = (base_gp / base_revenue * 100) if base_revenue else 0
        base_opex = self.base.get("Operating Expense", 0)

        rows = []
        for rev_chg in revenue_changes:
            for margin_chg in margin_changes:
                new_revenue = base_revenue * (1 + rev_chg)
                new_margin = base_margin + margin_chg
                new_gp = new_revenue * new_margin / 100
                new_oi = new_gp - base_opex
                new_ni = new_oi * 0.75
                rows.append({
                    "Revenue Change %": rev_chg * 100,
                    "Margin Change (bps)": margin_chg * 100,
                    "Revenue": new_revenue,
                    "Gross Profit": new_gp,
                    "Operating Income": new_oi,
                    "Net Income": new_ni,
                })
        return pd.DataFrame(rows)

    def tornado_data(
        self,
        drivers: list[str] | None = None,
        change_pct: float = 0.10,
        target: str = "Net Income",
    ) -> pd.DataFrame:
        """Tornado chart data: rank drivers by impact on target."""
        drivers = drivers or ["Total Revenue", "Cost Of Revenue", "Operating Expense"]
        base_target = self._compute_target(target, self.base)

        results = []
        for driver in drivers:
            if driver not in self.base.index:
                continue
            low = self._adjust_driver(driver, -change_pct)
            high = self._adjust_driver(driver, change_pct)
            low_target = self._compute_target(target, low)
            high_target = self._compute_target(target, high)
            results.append({
                "Driver": driver,
                "Low Case": low_target,
                "High Case": high_target,
                "Base": base_target,
                "Range": abs(high_target - low_target),
            })

        df = pd.DataFrame(results).sort_values("Range", ascending=False)
        return df

    def _compute_target(self, target: str, data: pd.Series) -> float:
        revenue = float(data.get("Total Revenue", 0))
        cogs = float(data.get("Cost Of Revenue", 0))
        opex = float(data.get("Operating Expense", 0))

        gross_profit = float(data.get("Gross Profit", revenue - cogs))
        operating_income = float(data.get("Operating Income", gross_profit - opex))

        if target == "Gross Profit":
            return gross_profit
        if target == "Operating Income":
            return operating_income
        if target == "Net Income":
            if "Net Income" in data.index and data.get("Total Revenue", 0) == self.base.get("Total Revenue", 0):
                base_ni = float(self.base.get("Net Income", 0))
                base_oi = float(self.base.get("Operating Income", 0))
                if base_oi != 0:
                    return operating_income * (base_ni / base_oi)
            return operating_income * 0.75
        return float(data.get(target, 0))
