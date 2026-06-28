import os
import yfinance as yf
import pandas as pd
from quantpairs.reusableModule.reusable_module import (
    drop_columns,
    rename_column,
    extract_target,
    combine_columns,
    drop_missing,
)

STOCKS = [
    "MSFT",
    "AAPL",
    "NVDA",
    "AVGO",
    "ORCL",
    "CRM",
    "ADBE",
    "AMD",
    "QCOM",
    "^GSPC",
    "^VIX",
]

data = yf.download(STOCKS, start="2018-01-01", end="2025-12-31", auto_adjust=True)


def make_dirs() -> None:
    """
    Make directories for the data to be downloaded
    """
    os.makedirs("data_files", exist_ok=True)
    os.makedirs("data_files/masterData", exist_ok=True)


def download_data(
    tickers: list, start_date: str, end_date: str, auto_adjust: bool
) -> None:
    """
    A function to donwnload daily stock data from Yahoo finance:
    Index : Date
    OPEN
    HIGH
    LOW
    CLOSE
    TICKER
    """

    for tick in tickers:
        data = yf.download(
            tick, start=start_date, end=end_date, auto_adjust=auto_adjust
        )
        # fname = tick.replace("^", "")
        fname = tick
        data.columns = data.columns.droplevel("Ticker")  # strip redundant header level
        data.index.name = "Date"
        data["Ticker"] = fname
        data.to_csv(f"data_files/{fname}.csv")


def close_data(data_frame: pd.DataFrame, column: list[str]):

    data_frame = drop_columns(data_frame, column)
    keys = data_frame.columns.values
    print("keys %s %s", keys, data_frame.iloc[0]["Ticker"])
    col_new_name = data_frame.iloc[0]["Ticker"] + "-" + keys[0]
    data_frame = rename_column(data_frame, "Close", col_new_name)
    data_frame = drop_columns(data_frame, keys[1])
    print("result %s", data_frame)

    return data_frame


def compute_return(prices: pd.Series) -> pd.Series:
    """Daily % return: (X_t - X_{t-1}) / X_{t-1} * 100."""
    return prices.pct_change() * 100


def add_calendar(data: pd.DataFrame) -> pd.DataFrame:
    """Append Year, Quarter, Month indicators from the Date index."""
    out = data.copy()
    out["Date"] = pd.to_datetime(out.index)
    out["Year"] = out["Date"].dt.year
    out["Quarter"] = out["Date"].dt.quarter
    out["Month"] = out["Date"].dt.month

    print("months", (out["Month"]))
    return out


def load_frame(ticker: str, data_dir: str = "data") -> pd.DataFrame:
    """Read one ticker CSV as a Date-indexed frame."""
    return pd.read_csv(f"{data_dir}/{ticker}.csv", index_col="Date", parse_dates=True)


def build_master_data(stocks: list = STOCKS, data_dir: str = "data") -> pd.DataFrame:
    """A function to create  a master data to use for analysis Per Stock:
    - Close price
            - Daily return — (Xₜ − Xₜ₋₁)/Xₜ₋₁ × 100
     **Market context (shared across all):**
            - S&P 500 daily return
            - VIX
     **Calendar indicators:**
            - Year
            - Quarter
            - Month
    **Index:**
            - Date (one row per trading day)
    """
    columns = {}

    for t in stocks:
        close = extract_target(load_frame(t, data_dir), "Close")
        columns[f"Close_{t}"] = close
        columns[f"Return_{t}"] = compute_return(close)

    columns["Return_SP500"] = compute_return(
        extract_target(load_frame("^GSPC", data_dir), "Close")
    )
    columns["^VIX"] = extract_target(load_frame("^VIX", data_dir), "Close")

    return drop_missing(add_calendar(combine_columns(columns)))


def main():

    make_dirs()
    download_data(STOCKS, "2018-01-01", "2025-12-31", True)
    data = "data_files"

    try:
        master = build_master_data(data_dir=data)
        master.to_csv("data_files/masterData/master_data.csv")
        print(f"master_data: {master.shape[0]} rows x {master.shape[1]} cols")
        print(master.head())
    except FileNotFoundError as fnf:
        print(" %s", fnf)


if __name__ == "__main__":
    main()
