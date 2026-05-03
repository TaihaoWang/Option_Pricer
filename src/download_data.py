import pandas as pd
import yfinance as yf


def download_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if data.empty:
        raise ValueError("No data downloaded. Check ticker or date format.")

    # yfinance >=0.2 returns MultiIndex columns like ('Close', 'SNDK') — flatten to 'Close'
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data[["Close"]].reset_index()
