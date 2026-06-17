"""Chart generation for financial analysis reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

PALETTE = {
    "primary": "#CC0000",
    "secondary": "#1a1a2e",
    "accent": "#e94560",
    "positive": "#2ecc71",
    "negative": "#e74c3c",
    "neutral": "#95a5a6",
    "forecast": "#3498db",
}

plt.rcParams.update({
    "figure.facecolor": "#fafafa",
    "axes.facecolor": "#ffffff",
    "axes.edgecolor": "#cccccc",
    "axes.labelcolor": "#333333",
    "text.color": "#333333",
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
})


def _save(fig: plt.Figure, path: Path, dpi: int = 150) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def _fmt_billions(x, _):
    if abs(x) >= 1e9:
        return f"${x/1e9:.1f}B"
    return f"${x/1e6:.0f}M"


def plot_revenue_profit_trend(income_stmt: pd.DataFrame, output_path: Path) -> None:
    metrics = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
    available = [m for m in metrics if m in income_stmt.columns]
    df = income_stmt[available].dropna(how="all")

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df.index.astype(str)
    width = 0.2
    colors = [PALETTE["secondary"], PALETTE["primary"], PALETTE["accent"], PALETTE["positive"]]

    for i, metric in enumerate(available):
        offset = (i - len(available) / 2 + 0.5) * width
        ax.bar([int(xi) + offset for xi in x], df[metric], width, label=metric, color=colors[i % len(colors)], alpha=0.85)

    ax.set_title("Tesla (TSLA) — Revenue & Profitability Trend")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Amount (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    _save(fig, output_path)


def plot_margin_trends(margins: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in margins.columns:
        ax.plot(margins.index, margins[col], marker="o", linewidth=2.5, label=col)
    ax.set_title("Tesla (TSLA) — Profit Margin Trends")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Margin (%)")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    _save(fig, output_path)


def plot_yoy_growth(growth: pd.DataFrame, output_path: Path) -> None:
    revenue_col = [c for c in growth.columns if "Total Revenue" in c]
    ni_col = [c for c in growth.columns if "Net Income" in c]
    cols = revenue_col + ni_col
    if not cols:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    df = growth[cols].dropna(how="all")
    x = np.arange(len(df))
    width = 0.35

    for i, col in enumerate(cols):
        vals = df[col].values
        colors = [PALETTE["positive"] if v >= 0 else PALETTE["negative"] for v in vals]
        ax.bar(x + i * width, vals, width, label=col.replace(" YoY %", ""), color=colors, alpha=0.85)

    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(df.index.astype(str))
    ax.set_title("Tesla (TSLA) — Year-over-Year Growth")
    ax.set_ylabel("Growth (%)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(0, color="gray", linewidth=0.8)
    _save(fig, output_path)


def plot_forecast(forecast_df: pd.DataFrame, metric: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    actual = forecast_df[forecast_df["Type"] == "Actual"]
    forecast = forecast_df[forecast_df["Type"] == "Forecast"]

    ax.plot(actual.index, actual[metric], "o-", color=PALETTE["primary"], linewidth=2.5, markersize=8, label="Actual")
    if not forecast.empty:
        connect_x = [actual.index[-1], forecast.index[0]]
        connect_y = [actual[metric].iloc[-1], forecast[metric].iloc[0]]
        ax.plot(connect_x, connect_y, "--", color=PALETTE["forecast"], alpha=0.5)
        ax.plot(forecast.index, forecast[metric], "s--", color=PALETTE["forecast"], linewidth=2.5, markersize=8, label="Forecast")

    ax.set_title(f"Tesla (TSLA) — {metric} Forecast")
    ax.set_xlabel("Year")
    ax.set_ylabel("Amount (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, output_path)


def plot_scenario_forecast(scenarios: pd.DataFrame, metric: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = {"Bear": PALETTE["negative"], "Base": PALETTE["neutral"], "Bull": PALETTE["positive"]}

    for scenario in scenarios["Scenario"].unique():
        data = scenarios[scenarios["Scenario"] == scenario]
        ax.plot(data["Year"], data[metric], "o-", linewidth=2.5, markersize=7,
                color=colors.get(scenario, PALETTE["secondary"]), label=scenario)

    ax.set_title(f"Tesla (TSLA) — {metric} Scenario Analysis")
    ax.set_xlabel("Year")
    ax.set_ylabel("Amount (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, output_path)


def plot_tornado(tornado_df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    base = tornado_df["Base"].iloc[0]
    y_pos = np.arange(len(tornado_df))

    for i, row in tornado_df.iterrows():
        low = row["Low Case"] - base
        high = row["High Case"] - base
        ax.barh(y_pos[tornado_df.index.get_loc(i)], low, left=base, color=PALETTE["negative"], alpha=0.7, height=0.5)
        ax.barh(y_pos[tornado_df.index.get_loc(i)], high, left=base, color=PALETTE["positive"], alpha=0.7, height=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tornado_df["Driver"])
    ax.axvline(base, color=PALETTE["secondary"], linewidth=2, linestyle="--", label=f"Base: {_fmt_billions(base, None)}")
    ax.set_title("Tesla (TSLA) — Sensitivity Tornado Chart (Net Income)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.legend()
    ax.grid(axis="x", alpha=0.3)
    _save(fig, output_path)


def plot_sensitivity_heatmap(two_way: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(
        two_way.astype(float) / 1e9,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=two_way.values.mean() / 1e9,
        ax=ax,
        cbar_kws={"label": "Net Income ($B)"},
    )
    ax.set_title("Tesla (TSLA) — Two-Way Sensitivity: Revenue vs OpEx → Net Income")
    _save(fig, output_path)


def plot_stock_price(price_history: pd.DataFrame, output_path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [3, 1]})

    ax1.plot(price_history.index, price_history["Close"], color=PALETTE["primary"], linewidth=1.5)
    ax1.fill_between(price_history.index, price_history["Close"], alpha=0.1, color=PALETTE["primary"])
    ax1.set_title("Tesla (TSLA) — Stock Price (5-Year)")
    ax1.set_ylabel("Price (USD)")
    ax1.grid(alpha=0.3)

    colors = [PALETTE["positive"] if c >= price_history["Open"].iloc[i] else PALETTE["negative"]
              for i, c in enumerate(price_history["Close"])]
    ax2.bar(price_history.index, price_history["Volume"], color=colors, alpha=0.5, width=1)
    ax2.set_ylabel("Volume")
    ax2.set_xlabel("Date")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    _save(fig, output_path)


def plot_budget_vs_actual(budget_summary: pd.DataFrame, output_path: Path) -> None:
    revenue_data = budget_summary[["Total Revenue", "Type"]].dropna()
    fig, ax = plt.subplots(figsize=(10, 5))

    actual = revenue_data[revenue_data["Type"] == "Actual"]
    budget = revenue_data[revenue_data["Type"] == "Budget"]

    ax.bar(actual.index.astype(str), actual["Total Revenue"], color=PALETTE["primary"], alpha=0.85, label="Actual")
    if not budget.empty:
        ax.bar(budget.index.astype(str), budget["Total Revenue"], color=PALETTE["forecast"], alpha=0.6, label="Budget")

    ax.set_title("Tesla (TSLA) — Revenue: Actual vs Budget")
    ax.set_ylabel("Amount (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    _save(fig, output_path)
