import pandas as pd
import numpy as np


def daily_returns(series: pd.Series) -> pd.Series:
    return series.pct_change().dropna()


def total_return(series: pd.Series) -> float:
    return series.iloc[-1] / series.iloc[0] - 1


def annualized_volatility(series: pd.Series, freq: int = 252) -> float:
    rets = daily_returns(series)
    return rets.std() * np.sqrt(freq)


def sharpe_ratio(series: pd.Series, risk_free: float = 0.0, freq: int = 252) -> float:
    rets = daily_returns(series)
    if rets.std().item() == 0:
        return np.nan

    mean_ret = rets.mean() * freq
    vol = rets.std() * np.sqrt(freq)
    return (mean_ret - risk_free) / vol


def max_drawdown(series: pd.Series) -> float:
    cum_max = series.cummax()
    drawdown = (series - cum_max) / cum_max
    return drawdown.min()
