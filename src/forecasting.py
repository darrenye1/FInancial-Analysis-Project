"""Revenue and earnings forecasting models."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class FinancialForecaster:
    """Forecast key financial metrics using time-series methods."""

    def __init__(self, income_stmt: pd.DataFrame):
        self.income_stmt = income_stmt

    def forecast_metric(
        self,
        metric: str = "Total Revenue",
        periods: int = 3,
        method: str = "exponential",
    ) -> pd.DataFrame:
        if metric not in self.income_stmt.columns:
            raise ValueError(f"Metric '{metric}' not found")

        series = self.income_stmt[metric].dropna().astype(float)
        years = series.index.tolist()
        values = series.values

        if method == "linear":
            forecast_vals = self._linear_forecast(values, periods)
        elif method == "cagr":
            forecast_vals = self._cagr_forecast(values, periods)
        else:
            forecast_vals = self._exponential_forecast(values, periods)

        last_year = years[-1]
        forecast_years = [last_year + i + 1 for i in range(periods)]

        result = pd.DataFrame({
            "Year": years + forecast_years,
            metric: list(values) + list(forecast_vals),
            "Type": ["Actual"] * len(years) + ["Forecast"] * periods,
        }).set_index("Year")
        return result

    @staticmethod
    def _linear_forecast(values: np.ndarray, periods: int) -> np.ndarray:
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        future_x = np.arange(len(values), len(values) + periods)
        return np.polyval(coeffs, future_x)

    @staticmethod
    def _cagr_forecast(values: np.ndarray, periods: int) -> np.ndarray:
        n = len(values) - 1
        cagr = (values[-1] / values[0]) ** (1 / n) - 1
        return np.array([values[-1] * (1 + cagr) ** (i + 1) for i in range(periods)])

    @staticmethod
    def _exponential_forecast(values: np.ndarray, periods: int) -> np.ndarray:
        if len(values) < 3:
            return FinancialForecaster._cagr_forecast(values, periods)
        try:
            model = ExponentialSmoothing(
                values, trend="add", seasonal=None, initialization_method="estimated"
            )
            fit = model.fit(optimized=True)
            return fit.forecast(periods)
        except Exception:
            return FinancialForecaster._cagr_forecast(values, periods)

    def multi_metric_forecast(
        self,
        metrics: list[str] | None = None,
        periods: int = 3,
    ) -> pd.DataFrame:
        metrics = metrics or ["Total Revenue", "Net Income", "Operating Income"]
        available = [m for m in metrics if m in self.income_stmt.columns]

        frames = []
        for m in available:
            fc = self.forecast_metric(m, periods=periods)
            frames.append(fc[[m, "Type"]].rename(columns={m: m}))

        result = frames[0]
        for f in frames[1:]:
            result = result.join(f.drop(columns=["Type"]), how="outer")
        return result

    def scenario_forecast(
        self,
        metric: str = "Total Revenue",
        periods: int = 3,
        scenarios: dict[str, float] | None = None,
    ) -> pd.DataFrame:
        """Bull / base / bear scenario forecasts."""
        scenarios = scenarios or {"Bear": -0.05, "Base": 0.10, "Bull": 0.25}
        series = self.income_stmt[metric].dropna().astype(float)
        last_val = series.iloc[-1]
        last_year = series.index[-1]

        rows = []
        for name, rate in scenarios.items():
            for i in range(1, periods + 1):
                year = last_year + i
                rows.append({
                    "Year": year,
                    "Scenario": name,
                    metric: last_val * (1 + rate) ** i,
                })
        return pd.DataFrame(rows)
