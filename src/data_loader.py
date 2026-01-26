# Data Loader

from __future__ import annotations
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ensures data from Yahoo Finance is in a Series not DataFrame
def _close_as_series(close_obj: pd.Series | pd.DataFrame, ticker: str) -> pd.Series:
    if isinstance(close_obj, pd.Series):
        return close_obj

    if isinstance(close_obj, pd.DataFrame):
        if close_obj.shape[1] == 1:
            return close_obj.iloc[:, 0]

        if ticker in close_obj.columns:
            return close_obj[ticker]

        raise ValueError(
            f"Expected a single Close column for {ticker}, but got columns: {list(close_obj.columns)}"
        )

    raise TypeError(f"Unexpected type for Close data: {type(close_obj)}")


# fetches and cleans data from yfinance
def fetch_yahoo(ticker: str, start: str = "2018-01-01") -> pd.Series:
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string")

    # downloads data from yfinance, adjusted for corporate action
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)

    if df is None or df.empty:
        raise ValueError(f"No data returned for ticker: {ticker}")

    # we will be using the closing price for BTC and ETH
    if "Close" not in df.columns:
        pass

    # Extract Close and GUARANTEE it is a Series
    close_obj = df["Close"].copy()
    s = _close_as_series(close_obj, ticker)

    # sorts by date and converts all indices to pandas datetime form
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()

    # fills all missing calendar days with last known price
    s = s.asfreq("D").ffill()

    # ensure numeric and no NaNs
    s = s.astype(float).dropna()

    # sanity check: prices should be positive
    if (s <= 0).any():
        raise ValueError("Non-positive prices found after data cleaning")

    s.name = ticker
    return s

# builds a price DataFrame from Yahoo Finance for multiple assets
def make_price_df(tickers: dict[str, str], start: str = "2018-01-01") -> pd.DataFrame:
    if not tickers or not isinstance(tickers, dict):
        raise ValueError("tickers must be a non-empty dict like {'btc_usd': 'BTC-USD'}")

    series_list: list[pd.Series] = []
    # downloads each asset one by one, iterates over both keys and values at the same time
    for col_name, yahoo_ticker in tickers.items():
        if not col_name or not isinstance(col_name, str):
            raise ValueError(f"Column name must be a non-empty string; got {col_name!r}")
        if not yahoo_ticker or not isinstance(yahoo_ticker, str):
            raise ValueError(f"Ticker must be a non-empty string; got {yahoo_ticker!r}")

        s = fetch_yahoo(yahoo_ticker, start=start).rename(col_name)
        series_list.append(s)

    # creates the table from each individual asset downloaded
    prices = pd.concat(series_list, axis=1).sort_index()

    if prices.empty:
        raise ValueError("Price DataFrame is empty after fetching data.")
    if prices.isna().any().any():
        prices = prices.ffill().dropna()

    return prices
def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    if prices is None or prices.empty:
        raise ValueError("prices must be a non-empty DataFrame")

    # ensures float values
    prices = prices.astype(float)

    # Compute log returns: r_t = log(P_t) - log(P_{t-1})
    log_prices = np.log(prices)
    returns = log_prices.diff()

    # drop the first row (NaN because there is no previous day)
    returns = returns.dropna()

    # renames columns - makes it explicit that they're returns
    returns.columns = [f"{c}_logret" for c in prices.columns]

    return returns
def save_prices_csv(prices: pd.DataFrame, filename="btc_eth_prices.csv") -> Path:
    if prices is None or prices.empty:
        raise ValueError("prices must be a non-empty DataFrame")

    out_path = ROOT / "data" / filename

    # confirms the data and directory exist
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # saves to the CSV we've already created
    prices.to_csv(out_path, index_label="date")

    return out_path

def load_prices_csv(filename="btc_eth_prices.csv") -> pd.DataFrame:
    path = ROOT / "data" / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Read CSV, parse the date column, and set it as index
    df = pd.read_csv(path, parse_dates=["date"])

    if "date" not in df.columns:
        raise ValueError("CSV must contain a 'date' column.")

    df = df.set_index("date").sort_index()

    if df.empty:
        raise ValueError("Loaded DataFrame is empty.")

    return df
