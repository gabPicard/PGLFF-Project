import yfinance as yf
import pandas as pd

def get_history(asset: str, period="1y", interval="1d") -> pd.DataFrame:
    df = yf.download(asset, period=period, interval=interval)
    df = df.reset_index()
    df.rename(columns={"Close": "price"}, inplace=True)
    df = df[["Date", "price"]]
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")
