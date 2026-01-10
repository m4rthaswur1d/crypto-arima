# Data Loader

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from __future__ import annotations

# fetches and cleans data from yfinance
def fetch_yahoo(ticker: str, start: str = "2018-01-01") -> pd.Series:
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be unempty string")

    # downloads data from yfinance, adjusted for corporate action
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)

    if df is None or df.empty:
        raise ValueError(f"No data returned for ticker: {ticker}")

    # we will be using the closing price for BTC and ETH, standard in finance
    if "Close" not in df.columns:
        raise ValueError(f"'Close' column missing for ticker: {ticker}")

    # sorts by date and converts all indices to pandas datetime form
    s = df["Close"].copy()
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()

    # fills all NaN values with the last known price
    s = s.asfreq("D").ffill()

    # drops NaN's and other consistencies that cannot be filled forward fill
    s = s.astype(float).dropna()
    if (s <= 0).any():
        raise ValueError("Non-positive prices found after data cleaning")

    s.name = ticker
    return s

def make_price_df(tickers: dict[str, str], start: str = "2018-01-01") -> pd.DataFrame:
def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
def save_prices_csv(prices: pd.DataFrame, filename="btc_eth_prices.csv") -> Path:
def load_prices_csv(filename="btc_eth_prices.csv") -> pd.DataFrame