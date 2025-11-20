import numpy as np
import pandas as pd


def compute_portfolio_returns(returns_df, weights):
    """Compute daily portfolio returns from asset returns and weights."""
    # Align weights with columns
    w = weights.reindex(returns_df.columns)
    portfolio_returns = (returns_df * w).sum(axis=1)
    portfolio_returns.name = "portfolio_returns"
    return portfolio_returns


def compute_cumulative_value(portfolio_returns, initial_value=100.0):
    """Compute cumulative portfolio value starting from initial_value."""
    cum_value = (1 + portfolio_returns).cumprod() * initial_value
    cum_value.name = "portfolio_value"
    return cum_value


def portfolio_stats(portfolio_returns, periods_per_year=252):
    """Compute annual return, annual volatility and approximate Sharpe ratio."""
    mean_daily = portfolio_returns.mean()
    vol_daily = portfolio_returns.std()

    mean_annual = mean_daily * periods_per_year
    vol_annual = vol_daily * np.sqrt(periods_per_year)
    if vol_annual == 0:
        sharpe = np.nan
    else:
        sharpe = mean_annual / vol_annual

    stats = {
        "Annual return (%)": mean_annual * 100,
        "Annual volatility (%)": vol_annual * 100,
        "Sharpe (approx)": sharpe,
    }

    return pd.DataFrame(stats, index=["Portfolio"])
