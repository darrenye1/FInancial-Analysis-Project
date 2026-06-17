"""Fetch financial data from Yahoo Finance."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


class FinancialDataFetcher:
    """Pull income statement, balance sheet, cash flow, and price history."""

    def __init__(self, ticker: str = "TSLA"):
        self.ticker = ticker.upper()
        self._stock = yf.Ticker(self.ticker)

    def get_company_info(self) -> dict:
        info = self._stock.info
        return {
            "name": info.get("longName", self.ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "employees": info.get("fullTimeEmployees", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "currency": info.get("currency", "USD"),
        }

    def get_income_statement(self) -> pd.DataFrame:
        df = self._stock.income_stmt
        return self._normalize_statement(df)

    def get_balance_sheet(self) -> pd.DataFrame:
        df = self._stock.balance_sheet
        return self._normalize_statement(df)

    def get_cash_flow(self) -> pd.DataFrame:
        df = self._stock.cashflow
        return self._normalize_statement(df)

    def get_price_history(self, period: str = "5y") -> pd.DataFrame:
        hist = self._stock.history(period=period)
        hist.index = pd.to_datetime(hist.index)
        return hist

    @staticmethod
    def _normalize_statement(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        out = df.copy()
        out.columns = pd.to_datetime(out.columns).year
        out = out.T.sort_index()
        out.index.name = "Year"
        return out

    def save_all(self, output_dir: str | Path) -> dict[str, Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = {}
        for name, getter in [
            ("income_statement", self.get_income_statement),
            ("balance_sheet", self.get_balance_sheet),
            ("cash_flow", self.get_cash_flow),
            ("price_history", self.get_price_history),
        ]:
            df = getter()
            path = output_dir / f"{self.ticker}_{name}.csv"
            df.to_csv(path)
            paths[name] = path
        return paths
